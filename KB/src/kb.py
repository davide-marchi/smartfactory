from owlready2 import *
from fastapi import FastAPI
import sympy
import json


ONTOLOGY_PATH = "../Ontology/sa_ontology.rdf"
TMP_ONTOLOGY_PATH = "../Ontology/tmp_ontology.rdf"
onto = get_ontology(ONTOLOGY_PATH).load()
app = FastAPI()

def get_kpi(kpi_id):
    query = f'*{kpi_id}'
    results = onto.search(iri = query)
    json_d = {'Status': -1}

    if len(results) == 0:
        return json_d

    for prop in results[0].get_properties():
        for value in prop[results[0]]:
            if isinstance(prop, DataPropertyClass):
                json_d[prop.name] = value
    
    json_d["Status"] = 0

    return json_d

def extract_datatype_properties(instance):
    """
    Extract datatype properties and their values from an instance.
    """
    datatype_data = {}
    for prop in onto.data_properties():  # Solo datatype properties
        value = prop[instance]  # Recupera il valore della proprietà per l'istanza
        if value:  # Controlla che la proprietà abbia un valore
            datatype_data[prop.name] = value[0]  # Assumiamo un singolo valore per proprietà
    return datatype_data

def get_all_kpis():
    """
    Retrieve all KPIs and their information as dict
    """
    # Recupera tutte le istanze di KPI
    all_kpis = {}
    for kpi in onto.KPI.instances():
        kpi_id = str(kpi.id[0])
        all_kpis[kpi_id] = extract_datatype_properties(kpi)

    return all_kpis

def get_all_machines():
    """
    Retrieve all machines and their information as dict
    """
    # Recupera tutte le istanze di KPI
    all_machines = {}
    for machine in onto.Machine.instances():
        machine_id = str(machine.id[0])
        all_machines[machine_id] = extract_datatype_properties(machine)

    return all_machines

def is_valid(kpi_info):
    def is_equal(formula1, formula2):
        formula1 = sympy.simplify(sympy.sympify(formula1))
        formula2 = sympy.simplify(sympy.sympify(formula2))

        return formula1 == formula2
    
    formula = kpi_info['atomic_formula'][0]

    for kpi in onto.KPI.instances():
        if kpi.formula[0] != '-' and formula != '-':
            if is_equal(kpi.atomic_formula[0], formula):
                return False
            
    return True

def rdf_to_txt(onto, output_file):
    def write_class_hierarchy(file, cls, indent=0):
        """
        Funzione ricorsiva per scrivere la gerarchia delle classi, comprese le sottoclassi.
        """
        file.write("  " * indent + f"Class: {cls.name}\n")
        
        # Scrivere le sottoclassi
        for subclass in cls.subclasses():
            write_class_hierarchy(file, subclass, indent + 1)
    
    with open(output_file, "w", encoding="utf-8") as file:
        # Scrivi tutte le classi
        file.write("Classes:\n")
        for cls in onto.classes():
            if cls != Thing:
                write_class_hierarchy(file, cls)

        # Scrivi tutte le proprietà (ObjectProperty, DataProperty, AnnotationProperty)
        file.write("\nProperties:\n")
        for prop in onto.properties():
            file.write(f"Property: {prop.name}\n")
            
            if isinstance(prop, ObjectPropertyClass):
                # Per le ObjectProperty, scriviamo dominio e range
                domain = prop.domain
                range_ = prop.range
                file.write(f"  Type: ObjectProperty\n")
                file.write(f"  Domain: {domain[0].name}\n")
                file.write(f"  Range: {range_[0].name}\n")
            elif isinstance(prop, DataPropertyClass):
                # Per le DataProperty, scriviamo anche il tipo del valore
                data_type = prop.range
                file.write(f"  Type: DataProperty\n")
                file.write(f"  Data Type: {data_type[0].__name__}\n")
            elif isinstance(prop, AnnotationPropertyClass):
                file.write("  Type: AnnotationProperty\n")

        # Scrivi tutti gli individui e le loro proprietà
        file.write("\nIndividuals:\n")
        for individual in onto.individuals():
            file.write(f"Individual: {individual.name}\n")
            
            # Itera sulle proprietà dell'individuo
            for prop in individual.get_properties():
                values = prop[individual]
                for value in values:
                    # Controlla se il valore è un oggetto o un valore letterale
                    if isinstance(value, Thing):  # Se il valore è un oggetto RDF
                        file.write(f"  {prop.name}: {value.name}\n")
                    else:  # Valore letterale (stringa, numero, ecc.)
                        file.write(f"  {prop.name}: {value}\n")

def add_kpi(kpi_info):
    if not is_valid(kpi_info):
        return False
    
    custom_class = onto.CustomKPItmp
    new_kpi = custom_class(kpi_info['id'][0], id=kpi_info['id'], description=kpi_info['description'], 
                           atomic_formula=kpi_info['atomic_formula'], formula=kpi_info['formula'], 
                           unit_measure=kpi_info['unit_measure'], forecastable=kpi_info['forecastable'], atomic=kpi_info['atomic'])
    
    #FIXME: add the object properties
    with onto:
        try:
            sync_reasoner()
            onto.save(file = TMP_ONTOLOGY_PATH, format = "rdfxml")
        except Exception as error:
            return False
    
    return True


if __name__ == "__main__":
    kpi_info = {
        'id': ['KPI_1'],
        'description': ['Test KPI'],
        'atomic_formula': ['(A + B) + C'],
        'formula': ['(A + B) + C'],
        'unit_measure': ['flfl'],
        'forecastable': [True],
        'atomic': [False]
    }

    add_kpi(kpi_info)

# -------------------------------------------- API Endpoints --------------------------------------------
@app.get("/get_kpi") 
async def get_kpi_endpoint(kpi_id: str):
    """
    Get KPI data by its ID via GET request.
    """
    kpi_data = get_kpi(kpi_id)
    if kpi_data["Status"] == -1:
        return {"error": "KPI not found"}

    return kpi_data

@app.get("/retrieve")
async def get_kpi_endpoint():
    """
    Get KPI data by its ID via GET request.
    """
    kpi_data = get_all_kpis()
    if not kpi_data:
        return {"error": "KPI not found"}
    return kpi_data