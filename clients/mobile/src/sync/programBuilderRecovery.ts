/** Reconcile the recorded command; no background POST or replacement key. */
import type {BuilderOutcome} from '../api/programBuilder';
import type {BuilderReceipt} from '../api/programBuilderDTO';
import type {PreparedBuilderCommand} from '../domain/programBuilderCommand';
import type {PendingBuilderCommand, ProgramBuilderPendingCommands} from '../storage/programBuilderPendingCommands';

export interface BuilderRecoveryClient {
  readonly ownerId: number; readonly backendScope: string;
  submit(command: PreparedBuilderCommand): Promise<BuilderOutcome<BuilderReceipt>>;
  status(command: PreparedBuilderCommand): Promise<BuilderOutcome<BuilderReceipt>>;
}
export class ProgramBuilderRecovery {
  private verified = new Set<string>();
  private busy = false;
  constructor(private client: BuilderRecoveryClient, private store: ProgramBuilderPendingCommands,
    private current: () => boolean) {
    if (client.ownerId !== store.ownerId || client.backendScope !== store.backendScope) throw Error('builder_partition_changed');
  }
  private owned(row: PreparedBuilderCommand): boolean {
    return this.current() && row.owner_id === this.client.ownerId && row.backend_scope === this.client.backendScope;
  }
  private key(row: PreparedBuilderCommand): string {return `${row.command_id}:${row.request_sha256}`;}
  private prepared(row: PendingBuilderCommand): PreparedBuilderCommand {
    const {owner_id, backend_scope, command_id, operation, program_id,
      expected_source_digest, payload_json, request_sha256} = row;
    return {owner_id, backend_scope, command_id, operation, program_id,
      expected_source_digest, payload_json, request_sha256};
  }
  private async exclusive(work: () => Promise<BuilderOutcome<BuilderReceipt>>): Promise<BuilderOutcome<BuilderReceipt>> {
    if (!this.current()) return {state: 'cancelled'};
    if (this.busy) throw Error('builder_command_busy');
    this.busy = true;
    try {return await work();}
    catch (error) {if (!this.current()) return {state: 'cancelled'}; throw error;}
    finally {this.busy = false;}
  }
  private async saved(command: PreparedBuilderCommand): Promise<PendingBuilderCommand | null> {
    if (!this.owned(command)) return null;
    const saved = await this.store.get(command.command_id, this.current);
    if (!saved || saved.payload_json !== command.payload_json || saved.request_sha256 !== command.request_sha256) throw Error('builder_command_missing');
    return this.owned(saved) ? saved : null;
  }
  private terminal(row: PendingBuilderCommand): BuilderOutcome<BuilderReceipt> | null {
    if (row.state === 'ACKED') return {state: 'confirmed', value: row.receipt!};
    if (row.state === 'REFUSED') return {state: 'rejected', status: row.rejection_status!, code: row.rejection};
    return null;
  }
  private async apply(row: PendingBuilderCommand, result: BuilderOutcome<BuilderReceipt>, initial = false): Promise<BuilderOutcome<BuilderReceipt>> {
    if (!this.owned(row)) return {state: 'cancelled'};
    if (result.state === 'confirmed') await this.store.ack(row.command_id, result.value, this.current);
    else if (initial && result.state === 'rejected' && result.code !== null) {
      // A fresh POST's exact pre-effect refusal is distinct from a lookup/retry
      // refusal, which says nothing about a previously unknown mutation.
      await this.store.refuse(row.command_id, row.request_sha256, result.code, result.status, this.current);
    }
    return this.current() ? result : {state: 'cancelled'};
  }
  send(body: unknown): Promise<BuilderOutcome<BuilderReceipt>> {return this.exclusive(async () => {
    const row = await this.store.prepare(body, this.current);
    const terminal = this.terminal(row); if (terminal) return terminal;
    if (row.state !== 'PREPARED') throw Error('builder_verification_required');
    await this.store.markUnknown(row.command_id, row.request_sha256, this.current);
    const durable = await this.saved(row); if (!durable) return {state: 'cancelled'};
    return this.apply(durable, await this.client.submit(this.prepared(durable)), true);
  });}
  verify(command: PendingBuilderCommand): Promise<BuilderOutcome<BuilderReceipt>> {return this.exclusive(async () => {
    const row = await this.saved(command); if (!row) return {state: 'cancelled'};
    const terminal = this.terminal(row); if (terminal) return terminal;
    this.verified.delete(this.key(row));
    const result = await this.client.status(this.prepared(row));
    if (!this.owned(row)) return {state: 'cancelled'};
    if (result.state === 'unknown') this.verified.add(this.key(row));
    return this.apply(row, result);
  });}
  replay(command: PendingBuilderCommand): Promise<BuilderOutcome<BuilderReceipt>> {return this.exclusive(async () => {
    if (!this.owned(command)) return {state: 'cancelled'};
    if (!this.verified.delete(this.key(command))) throw Error('builder_verification_required');
    const row = await this.saved(command); if (!row) return {state: 'cancelled'};
    if (!['PREPARED', 'SENT_UNKNOWN'].includes(row.state)) throw Error('builder_command_not_pending');
    await this.store.markUnknown(row.command_id, row.request_sha256, this.current, false);
    const durable = await this.saved(row); if (!durable) return {state: 'cancelled'};
    return this.apply(durable, await this.client.submit(this.prepared(durable)));
  });}
}
