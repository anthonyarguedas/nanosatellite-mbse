package CADModel {
    private import ScalarValues::*;
    private import ControlFunctions::*;
    private import SequenceFunctions::*;
    doc /* Selected scope is EPS architecture review and verified connector wiring.
     * Initial target is KiCad 10.0.7, schematic format 20260306. A future exporter
     * may instantiate pinned native templates. No generator or layout is modeled.
     * https://docs.kicad.org/10.0/en/cli/cli.html
     * https://dev-docs.kicad.org/en/file-formats/sexpr-schematic/
     * https://dev-docs.kicad.org/en/apis-and-binding/ipc-api/for-addon-developers/
     * Occurrence identity is HardwareComponent.physical_resource_id. Product
     * identity is its catalog_product_id. Views reference those existing parts.
     * One physical occurrence owns its BOM entry. Internal elements and repeated
     * views refer to that owner. Unselected logical views need no BOM entry.
     * BOM quantities and export references are derived. Port IDs are view scoped.
     * Unknown pinouts remain logical, with absent footprint, on_board false and
     * exclude_from_sim true. Logical identifiers are never physical pin numbers.
     * Power and return use separate nets. Electrical data members use individual
     * nets. A graphical interface bundle has no electrical net membership claim.
     * Verified pins retain their source records and native symbol pin semantics.
     * Controller circuits, PCB transfer and simulation require a separate review.
     */
    enum def SchematicRepresentation { architecture_black_box; connector_wiring; controller_circuit; }
    enum def InterfaceKind :> String {
        enum power = "power";
        enum return_path = "return";
        enum data = "data";
        enum enable = "enable";
        enum fault = "fault";
        enum telemetry = "telemetry";
    }
    enum def PinMappingStatus { logical; verified_physical; }
    attribute def LogicalPort {
        attribute port_id : String;
        attribute catalog_element_id : String[0..1];
        attribute interface_kind : InterfaceKind;
        attribute direction : CatalogModel::PinDirection;
        attribute connected_net_id : String[0..1];
        attribute pin_mapping_status : PinMappingStatus;
        attribute physical_pin : CatalogModel::PinRecord[0..1];
    }
    attribute def ElectricalNet {
        attribute net_id : String;
        attribute net_kind : InterfaceKind;
        attribute return_net_id : String[0..1];
    }
    attribute def OccurrenceView {
        attribute view_id : String;
        ref part hardware : EPSModel::HardwareComponent;
        ref part bom_owner : EPSModel::HardwareComponent;
        attribute representation : SchematicRepresentation;
        attribute ports : LogicalPort[0..*];
        attribute in_bom : Boolean;
        attribute on_board : Boolean = false;
        attribute exclude_from_sim : Boolean = true;
        attribute footprint_library_id : String[0..1];
        attribute symbol_resource : CatalogModel::ResourceRecord[0..1];
    }
    attribute def BOMEntry {
        ref part owner : EPSModel::HardwareComponent;
        attribute owning_view_id : String;
    }
    part def ElectricalArchitecture {
        attribute views : OccurrenceView[0..*];
        attribute nets : ElectricalNet[0..*];
        attribute bom_entries : BOMEntry[0..*];
        ref part catalog : CatalogModel::Catalog[0..1];
        assert constraint occurrenceIdentity {
            views->forAll { in a : OccurrenceView;
                size(a.hardware.physical_resource_id) == 1 and size(a.bom_owner.physical_resource_id) == 1 and
                views->forAll { in b : OccurrenceView;
                    (a == b or a.view_id != b.view_id) and
                    (a.hardware == b.hardware or
                     a.hardware.physical_resource_id != b.hardware.physical_resource_id) and
                    (a.hardware != b.hardware or a.bom_owner == b.bom_owner) and
                    (a.hardware == b.bom_owner or
                     a.hardware.physical_resource_id != b.bom_owner.physical_resource_id) and
                    (a.bom_owner == b.bom_owner or
                     a.bom_owner.physical_resource_id != b.bom_owner.physical_resource_id) } }
        }
        assert constraint oneBOMEntryPerOccurrence {
            bom_entries->forAll { in a : BOMEntry;
                size(a.owner.physical_resource_id) == 1 and size(a.owner.catalog_product_id) == 1 and
                bom_entries->forAll { in b : BOMEntry;
                    a == b or a.owner.physical_resource_id != b.owner.physical_resource_id } and
                size(views->select { in v : OccurrenceView;
                    v.view_id == a.owning_view_id and v.hardware == a.owner and
                    v.bom_owner == a.owner and v.in_bom }) == 1 }
        }
        assert constraint viewBOMMembership {
            views->forAll { in v : OccurrenceView;
                not v.in_bom or (v.hardware == v.bom_owner and
                    bom_entries->exists { in item_record : BOMEntry;
                        item_record.owner == v.hardware and item_record.owning_view_id == v.view_id }) }
        }
        assert constraint architecturePolicy {
            views->forAll { in v : OccurrenceView;
                not v.on_board and v.exclude_from_sim and size(v.footprint_library_id) == 0 and
                v.representation != SchematicRepresentation::controller_circuit }
        }
        assert constraint uniqueLogicalNets {
            nets->forAll { in a : ElectricalNet; nets->forAll { in b : ElectricalNet;
                a == b or a.net_id != b.net_id } }
        }
        assert constraint logicalConnectivity {
            views->forAll { in v : OccurrenceView;
                v.ports->forAll { in p : LogicalPort;
                    v.ports->forAll { in q : LogicalPort; p == q or p.port_id != q.port_id } and
                    p.connected_net_id->forAll { in id : String;
                        nets->exists { in n : ElectricalNet;
                            n.net_id == id and n.net_kind == p.interface_kind } } } }
        }
        assert constraint separatePowerReturns {
            nets->forAll { in n : ElectricalNet;
                (n.net_kind != InterfaceKind::power or size(n.return_net_id) == 1) and
                n.return_net_id->forAll { in id : String;
                    id != n.net_id and nets->exists { in r : ElectricalNet;
                        r.net_id == id and r.net_kind == InterfaceKind::return_path } } }
        }
        assert constraint verifiedPhysicalPins {
            views->forAll { in v : OccurrenceView;
                v.ports->forAll { in p : LogicalPort;
                    (p.pin_mapping_status == PinMappingStatus::verified_physical) == (size(p.physical_pin) == 1) and
                    (p.pin_mapping_status != PinMappingStatus::verified_physical or
                        (size(catalog) == 1 and size(v.hardware.catalog_product_id) == 1 and
                         size(p.catalog_element_id) == 1)) and
                    p.physical_pin->forAll { in pin : CatalogModel::PinRecord;
                        pin.product_id == v.hardware.catalog_product_id and
                        pin.element_id == p.catalog_element_id and
                        (pin.pin_kind != CatalogModel::PinKind::no_connect or size(p.connected_net_id) == 0) and
                        catalog->forAll { in c : CatalogModel::Catalog;
                            c.pins->exists { in verified : CatalogModel::PinRecord; verified == pin } } } } }
        }
        assert constraint connectorPinCoverage {
            views->forAll { in v : OccurrenceView;
                v.representation != SchematicRepresentation::connector_wiring or
                v.ports->forAll { in p : LogicalPort;
                    size(p.connected_net_id) == 0 or
                    p.pin_mapping_status == PinMappingStatus::verified_physical } }
        }
        assert constraint checkedSymbolResources {
            views->forAll { in v : OccurrenceView;
                v.symbol_resource->forAll { in resource : CatalogModel::ResourceRecord;
                    resource.resource_kind == CatalogModel::ResourceKind::symbol and
                    size(catalog) == 1 and size(v.hardware.catalog_product_id) == 1 and
                    resource.product_id == v.hardware.catalog_product_id and
                    catalog->forAll { in c : CatalogModel::Catalog;
                        c.resources->exists { in verified : CatalogModel::ResourceRecord; verified == resource } } } }
        }
        doc /* Optional physical pin binding uses a verified catalog pin record for
         * the exact product/element. Missing mapping is distinct from verified NC.
         * Partial mapping does not make pin_map_complete true. This architecture
         * graph supplies no spacecraft wiring, release success or readiness claim.
         */
    }
}
