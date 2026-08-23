# Assumption Registry View

Source: controlling specification, Section 2.4.

Every `A-*` assumption is serialized with one of `satisfied`, `failed`,
`not_identifiable`, `not_applicable`, or `deferred`. GRV0 initializes scientific
assumptions as `deferred`; baseline and package-admission facts are recorded
separately and do not count as theory evidence.
