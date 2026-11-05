import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
const { DatabaseSync } = require('node:sqlite');
/** Real SQLite port matching the actual async storage boundary, no SQL mocked. */
export class SqliteFile {
  readonly folder=mkdtempSync(join(tmpdir(),'auren-data-integration-'));
  readonly path=join(this.folder,'owners.db');
  db:any=new DatabaseSync(this.path);
  port():any{
    const db=this.db;
    const port={execAsync:async(sql:string)=>{db.exec(sql);},
      getFirstAsync:async(sql:string,...values:any[])=>db.prepare(sql).get(...values)??null,
      runAsync:async(sql:string,...values:any[])=>db.prepare(sql).run(...values),
      withExclusiveTransactionAsync:async(action:(tx:any)=>Promise<void>)=>{
        db.exec('BEGIN IMMEDIATE');try{await action(port);db.exec('COMMIT');}catch(e){db.exec('ROLLBACK');throw e;}
      }};return port;
  }
  reopen(){this.db.close();this.db=new DatabaseSync(this.path);}
  close(){this.db.close();rmSync(this.folder,{recursive:true,force:true});}
}
