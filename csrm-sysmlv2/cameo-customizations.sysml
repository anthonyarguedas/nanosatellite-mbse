// Native SysML v2 item type for 2025 Cameo editor settings.
// Href values retain source identity. They do not assert native profile typing.
package CSRMCameoCustomization {
    item def EditorCustomization {
        attribute sourceClassRef : ScalarValues::String;
        attribute sourceApplicationRef : ScalarValues::String;
        attribute customizationTarget : ScalarValues::String [0..*];
        attribute quickApplyingFor : ScalarValues::String [0..*];
        attribute preferredMetatype : ScalarValues::String [0..*];
        attribute superTypes : ScalarValues::String [0..*];
        attribute typesForSource : ScalarValues::String [0..*];
        attribute typesForTarget : ScalarValues::String [0..*];
        attribute hiddenOwnedTypes : ScalarValues::String [0..*];
        attribute hideMetatype : ScalarValues::Boolean [0..1];
        attribute sourceComment : ScalarValues::String [0..1];
    }
}
