'use strict';
// Binary stdin = 32-byte key followed by data; never key material in argv/logs.
const crypto = require('node:crypto');
const fs = require('node:fs');
const MAX = 256 * 1024 * 1024 + 65536;
const MAGIC = Buffer.from('AURENQPF');
try {
  const chunks = [];
  let length = 0;
  for (;;) {
    const chunk = Buffer.alloc(65536);
    const count = fs.readSync(0, chunk, 0, chunk.length, null);
    if (!count) break;
    length += count;
    if (length > MAX + 128) throw Error();
    chunks.push(chunk.subarray(0, count));
  }
  const input = Buffer.concat(chunks);
  const key = input.subarray(0, 32);
  const data = input.subarray(32);
  if (key.length !== 32) throw Error();
  let result;
  if (process.argv[2] === 'encrypt') {
    if (data.length > MAX) throw Error();
    // Authenticated fixed header: magic(8), version(1), size(8), nonce(12).
    const header = Buffer.alloc(29);
    MAGIC.copy(header);
    header[8] = 1;
    header.writeBigUInt64BE(BigInt(data.length), 9);
    crypto.randomBytes(12).copy(header, 17);
    const cipher = crypto.createCipheriv('aes-256-gcm', key, header.subarray(17));
    cipher.setAAD(header);
    result = Buffer.concat([header, cipher.update(data), cipher.final(), cipher.getAuthTag()]);
  } else if (process.argv[2] === 'decrypt') {
    if (data.length < 45 || !data.subarray(0, 8).equals(MAGIC) || data[8] !== 1) throw Error();
    const header = data.subarray(0, 29);
    const size = header.readBigUInt64BE(9);
    if (size > BigInt(MAX) || size !== BigInt(data.length - 45)) throw Error();
    const cipher = crypto.createDecipheriv('aes-256-gcm', key, header.subarray(17));
    cipher.setAAD(header);
    cipher.setAuthTag(data.subarray(-16));
    // No bytes emitted before final authentication succeeds.
    result = Buffer.concat([cipher.update(data.subarray(29, -16)), cipher.final()]);
  } else throw Error();
  fs.writeFileSync(1, result);
} catch {
  process.stderr.write('qa_proof_crypto_refused\n');
  process.exitCode = 1;
}
