pii_order = 6
generator_threshold = 1.2e-8
general_generator_threshold = 1.2e-8


class TableNames:
    PII = "PII"
    pwrepresentation = "pwrepresentation"
    representation_frequency = "representation_frequency"
    pwrepresentation_frequency = "pwrepresentation_frequency"
    pwrepresentation_unique = "PwRepresentation_unique"
    pwrepresentation_general = f"{pwrepresentation}_general"
    representation_frequency_base_general = f"representation_frequency_base_general"
    representation_frequency_general = f"{representation_frequency}_general"
    pwrepresentation_frequency_general = f"{pwrepresentation_frequency}_general"
    pwrepresentation_unique_general = f"{pwrepresentation_unique}_general"


class RFParams:
    n_estimators = 30
    criterion = 'entrpy'
    min_samples_leaf = 10
    max_features = 0.8