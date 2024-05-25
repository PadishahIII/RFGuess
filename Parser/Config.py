pii_order = 6
generator_threshold = 1.2e-8 # deprecated
general_generator_threshold = 1.2e-8

DatabaseUrl = "mysql://root:914075@localhost/rfguess"


class TableNames:
    PII = "pii"
    pwrepresentation = "pwrepresentation"
    representation_frequency = "representation_frequency"
    pwrepresentation_frequency = "pwrepresentation_frequency"
    pwrepresentation_unique = "pwrepresentation_unique"
    pwrepresentation_general = f"{pwrepresentation}_general"
    representation_frequency_base_general = f"representation_frequency_base_general"
    representation_frequency_general = f"{representation_frequency}_general"
    pwrepresentation_frequency_general = f"{pwrepresentation_frequency}_general"
    pwrepresentation_unique_general = f"{pwrepresentation_unique}_general"

    generalTables = [PII,
                     pwrepresentation_general,
                     pwrepresentation_frequency_general,
                     representation_frequency_general,
                     representation_frequency_base_general,
                     pwrepresentation_unique_general]


class RFParams:
    n_estimators = 30
    criterion = 'gini'
    min_samples_leaf = 10
    max_features = 0.8
