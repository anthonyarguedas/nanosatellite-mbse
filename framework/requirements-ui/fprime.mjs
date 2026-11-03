import { validateWorkspace } from './model.mjs';

const tutorial = 'https://fprime.jpl.nasa.gov/latest/tutorials-math-component/docs/math-component/';
const comment = value => String(value).replace(/[\r\n]/g, ' ');

export function renderFprimeFiles(workspace, context, { catalog, products }) {
  validateWorkspace(workspace, catalog, products);
  const owner = workspace.elements.find(row => row.key === context);
  if (!owner || catalog.find(type => type.model === owner.definition)?.role !== 'eps') throw new Error('Choose an EPS tab to export.');
  const components = workspace.components.filter(row => row.owner === context);
  if (!components.length) throw new Error('Add at least one COTS component before exporting.');
  const byId = new Map(products.map(product => [product.id, product]));
  const statements = new Map(workspace.statements.map(row => [row.key, row.id]));
  const files = new Map(), manifest = [];
  for (const row of components) {
    const product = byId.get(row.product);
    const suffix = product.partNumber.replace(/[^A-Za-z0-9]+/g, '_').replace(/^_+|_+$/g, '').slice(0, 60);
    const name = `Component_${row.id}_${suffix}`, path = `EpsComponents/${name}`;
    const requirements = row.requirements.map(key => statements.get(key));
    manifest.push({ id: row.id, key: row.key, product: row.product, manufacturer: product.manufacturer,
      partNumber: product.partNumber, requirements, namespace: 'Eps', component: name, path });
    files.set(`${path}/${name}.fpp`, `# Generated from the EPS COTS component table.
# Product: ${comment(product.partNumber)} (${comment(product.manufacturer)})
# Catalog ID: ${row.product}
# Physical instance: ${row.key}
# Affected requirements: ${requirements.join(', ') || 'None linked'}
# Tutorial: ${tutorial}
module Eps {
  @ Software wrapper for ${comment(product.partNumber)}. Hardware behavior remains to be implemented.
  active component ${name} {
    @ Command receive port
    command recv port cmdIn
    @ Command registration port
    command reg port cmdRegOut
    @ Command response port
    command resp port cmdResponseOut
    @ Event port
    event port eventOut
    @ Text event port
    text event port textEventOut
    @ Time get port
    time get port timeGetOut

    @ Exercise the software wrapper without performing hardware operations
    async command NO_OP()

    @ The software wrapper received NO_OP
    event NoOpReceived() severity activity low format "NO_OP received"
  }
}
`);
    files.set(`${path}/${name}.hpp`, `#pragma once

#include "${path}/${name}ComponentAc.hpp"

namespace Eps {

//! Software wrapper only. Add reviewed hardware ports and behavior to the FPP model.
class ${name} final : public ${name}ComponentBase {
  public:
    explicit ${name}(const char* const compName);
    ~${name}() override;

  private:
    void NO_OP_cmdHandler(FwOpcodeType opCode, U32 cmdSeq) override;
};

}  // namespace Eps
`);
    files.set(`${path}/${name}.cpp`, `#include "${path}/${name}.hpp"

namespace Eps {

${name}::${name}(const char* const compName)
    : ${name}ComponentBase(compName) {}

${name}::~${name}() = default;

void ${name}::NO_OP_cmdHandler(FwOpcodeType opCode, U32 cmdSeq) {
    // This command confirms software dispatch only. It does not verify hardware.
    this->log_ACTIVITY_LO_NoOpReceived();
    this->cmdResponse_out(opCode, cmdSeq, Fw::CmdResponse::OK);
}

}  // namespace Eps
`);
    files.set(`${path}/CMakeLists.txt`, `set(SOURCE_FILES
    "${name}.fpp"
    "${name}.cpp"
)
register_fprime_module()
`);
  }
  files.set('EpsComponents/CMakeLists.txt', manifest.map(row => `add_fprime_subdirectory(\u0024{CMAKE_CURRENT_LIST_DIR}/${row.component}/)`).join('\n') + '\n');
  files.set('components.json', JSON.stringify({ eps: owner.id, context, tutorial, components: manifest }, null, 2) + '\n');
  files.set('README.md', `# EPS F-Prime component boilerplate

Source tutorial: ${tutorial}

This archive declares one active F-Prime software wrapper for each selected COTS instance in this EPS table. Repeated products have separate component declarations. The manifest maps each declaration to its physical row and affected requirement IDs.

## Add to an existing F-Prime project

1. Copy EpsComponents/ into the project root, beside Components/.
2. Add this line to the project's root CMakeLists.txt:

\u0060\u0060\u0060cmake
add_fprime_subdirectory(\u0024{CMAKE_CURRENT_LIST_DIR}/EpsComponents/)
\u0060\u0060\u0060

3. Run \u0060fprime-util generate\u0060 at the project root if a build cache does not exist. Run \u0060fprime-util build\u0060.
4. Each component includes its FPP model, C++ header, C++ source and CMake registration. After editing an FPP model, run \u0060fprime-util impl\u0060 inside that component's directory and review the generated .template.hpp and .template.cpp files before merging changes.
5. Add instances and connections to your deployment. Choose base IDs, queue sizes, stack sizes and task priorities for your mission. Connect command, event and time services using the normal F-Prime topology patterns.

## Scope

The NO_OP command logs receipt and returns a software command response. It performs no hardware access. Add hardware ports, drivers, commands, telemetry and tests after reviewing the part's datasheet and mission requirements. Requirement links provide traceability. They do not establish flight readiness or generated driver correctness.

Generated base classes and framework code are supplied by your F-Prime toolchain. This archive is a set of project modules, not a complete deployment.
`);
  return files;
}

const crcTable = Uint32Array.from({ length: 256 }, (_, index) => {
  let value = index;
  for (let bit = 0; bit < 8; bit++) value = value & 1 ? 0xedb88320 ^ (value >>> 1) : value >>> 1;
  return value >>> 0;
});
const crc32 = bytes => {
  let crc = 0xffffffff;
  for (const byte of bytes) crc = crcTable[(crc ^ byte) & 255] ^ (crc >>> 8);
  return (crc ^ 0xffffffff) >>> 0;
};

// ZIP STORE keeps the download dependency free and readable by standard tools.
export function renderFprimeArchive(workspace, context, options) {
  const files = renderFprimeFiles(workspace, context, options), local = [], central = [];
  let offset = 0;
  for (const [path, source] of files) {
    const name = Buffer.from(path), content = Buffer.from(source), crc = crc32(content);
    const header = Buffer.alloc(30);
    header.writeUInt32LE(0x04034b50, 0); header.writeUInt16LE(20, 4); header.writeUInt16LE(0x800, 6);
    header.writeUInt16LE(33, 12); header.writeUInt32LE(crc, 14);
    header.writeUInt32LE(content.length, 18); header.writeUInt32LE(content.length, 22); header.writeUInt16LE(name.length, 26);
    local.push(header, name, content);
    const entry = Buffer.alloc(46);
    entry.writeUInt32LE(0x02014b50, 0); entry.writeUInt16LE(20, 4); entry.writeUInt16LE(20, 6); entry.writeUInt16LE(0x800, 8);
    entry.writeUInt16LE(33, 14); entry.writeUInt32LE(crc, 16);
    entry.writeUInt32LE(content.length, 20); entry.writeUInt32LE(content.length, 24); entry.writeUInt16LE(name.length, 28); entry.writeUInt32LE(offset, 42);
    central.push(entry, name); offset += header.length + name.length + content.length;
  }
  const directory = Buffer.concat(central), end = Buffer.alloc(22);
  end.writeUInt32LE(0x06054b50, 0); end.writeUInt16LE(files.size, 8); end.writeUInt16LE(files.size, 10);
  end.writeUInt32LE(directory.length, 12); end.writeUInt32LE(offset, 16);
  return Buffer.concat([...local, directory, end]);
}
