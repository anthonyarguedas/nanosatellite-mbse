import type { KiCadFile } from './index';

const encoder = new TextEncoder();
function crc32(bytes: Uint8Array): number {
  let crc = 0xffffffff;
  for (const byte of bytes) {
    crc ^= byte;
    for (let bit = 0; bit < 8; bit++) crc = (crc >>> 1) ^ (0xedb88320 & -(crc & 1));
  }
  return (crc ^ 0xffffffff) >>> 0;
}
function header(size: number): { bytes: Uint8Array; view: DataView } {
  const bytes = new Uint8Array(size);
  return { bytes, view: new DataView(bytes.buffer) };
}

/** Small, deterministic, uncompressed UTF-8 ZIP. No runtime dependency or backend. */
export function createKiCadZip(files: readonly KiCadFile[]): Uint8Array {
  if (files.length > 65535) throw new Error('Too many ZIP entries.');
  const names = new Set<string>();
  const local: Uint8Array[] = [], central: Uint8Array[] = [];
  let offset = 0;
  for (const file of files) {
    if (!/^[a-zA-Z0-9][a-zA-Z0-9._-]*$/.test(file.name) || names.has(file.name)) throw new Error('ZIP entries must have unique safe base names.');
    names.add(file.name);
    const name = encoder.encode(file.name), data = encoder.encode(file.content);
    const crc = crc32(data);
    if (data.length > 0xffffffff || offset + data.length > 0xffffffff) throw new Error('ZIP64 archives are unsupported.');
    const l = header(30);
    l.view.setUint32(0, 0x04034b50, true);
    l.view.setUint16(4, 20, true);
    l.view.setUint16(6, 0x800, true);
    l.view.setUint16(12, 33, true); // 1980-01-01, deterministic DOS date.
    l.view.setUint32(14, crc, true);
    l.view.setUint32(18, data.length, true);
    l.view.setUint32(22, data.length, true);
    l.view.setUint16(26, name.length, true);
    local.push(l.bytes, name, data);
    const c = header(46);
    c.view.setUint32(0, 0x02014b50, true);
    c.view.setUint16(4, 20, true);
    c.view.setUint16(6, 20, true);
    c.view.setUint16(8, 0x800, true);
    c.view.setUint16(14, 33, true);
    c.view.setUint32(16, crc, true);
    c.view.setUint32(20, data.length, true);
    c.view.setUint32(24, data.length, true);
    c.view.setUint16(28, name.length, true);
    c.view.setUint32(42, offset, true);
    central.push(c.bytes, name);
    offset += l.bytes.length + name.length + data.length;
  }
  const centralSize = central.reduce((sum, bytes) => sum + bytes.length, 0);
  if (offset + centralSize + 22 > 0xffffffff) throw new Error('ZIP64 archives are unsupported.');
  const end = header(22);
  end.view.setUint32(0, 0x06054b50, true);
  end.view.setUint16(8, files.length, true);
  end.view.setUint16(10, files.length, true);
  end.view.setUint32(12, centralSize, true);
  end.view.setUint32(16, offset, true);
  const result = new Uint8Array(offset + centralSize + end.bytes.length);
  let cursor = 0;
  for (const chunk of [...local, ...central, end.bytes]) { result.set(chunk, cursor); cursor += chunk.length; }
  return result;
}
