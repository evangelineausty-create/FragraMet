
from cobra import Model, Reaction, Metabolite


def run_fba(substrate_uptake=10.0):
    # Create a simplified demonstration model
    model = Model("FragraMet_Demo")

    # Define metabolites
    ferulic = Metabolite(
        "ferulic_c",
        name="Ferulic Acid",
        compartment="c"
    )

    feruloyl_coa = Metabolite(
        "feruloyl_coa_c",
        name="Feruloyl-CoA",
        compartment="c"
    )

    vanillin = Metabolite(
        "vanillin_c",
        name="Vanillin",
        compartment="c"
    )

    # Ferulic acid supply
    uptake = Reaction("FERULIC_SUPPLY")
    uptake.name = "Ferulic Acid Supply"
    uptake.lower_bound = 0
    uptake.upper_bound = substrate_uptake
    uptake.add_metabolites({
        ferulic: 1
    })

    # Ferulic acid to Feruloyl-CoA
    reaction1 = Reaction("FCS")
    reaction1.name = "Feruloyl-CoA Formation"
    reaction1.lower_bound = 0
    reaction1.upper_bound = 1000
    reaction1.add_metabolites({
        ferulic: -1,
        feruloyl_coa: 1
    })

    # Feruloyl-CoA to Vanillin
    reaction2 = Reaction("ECH")
    reaction2.name = "Vanillin Formation"
    reaction2.lower_bound = 0
    reaction2.upper_bound = 1000
    reaction2.add_metabolites({
        feruloyl_coa: -1,
        vanillin: 1
    })

    # Vanillin export
    export = Reaction("VANILLIN_EXPORT")
    export.name = "Vanillin Export"
    export.lower_bound = 0
    export.upper_bound = 1000
    export.add_metabolites({
        vanillin: -1
    })

    # Add reactions
    model.add_reactions([
        uptake,
        reaction1,
        reaction2,
        export
    ])

    # Objective: maximize vanillin export
    model.objective = "VANILLIN_EXPORT"

    # Solve the FBA optimization problem
    solution = model.optimize()

    return {
        "status": solution.status,
        "vanillin_flux": solution.objective_value,
        "reaction_fluxes": solution.fluxes.to_dict()
    }


if __name__ == "__main__":
    result = run_fba()

    print("FBA Status:", result["status"])
    print("Predicted Vanillin Flux:", result["vanillin_flux"])
    print("Reaction Fluxes:", result["reaction_fluxes"])
