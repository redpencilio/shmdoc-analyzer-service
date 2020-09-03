
supported_units_map = {
    "degrees_celsius" : "http://vocab.nerc.ac.uk/collection/P06/current/UPAA/"
}

def get_unit_by_uri(uri):
    for name, unit_uri in supported_units_map.items():
        print(name, unit_uri, uri)
        if (uri == unit_uri):
            print(name)
            return name
    return None

def elements_sub_zero(column):
    counter = 0
    print(column)
    for el in range(1, len(column)):
        print(column[el])
        if column[el] < 0:
            counter += 1
    
    return {"name": "Freezing count (<0 degC)", "value" : counter}

def analyze_celsius(data):
    """
    @param data = 1 column
    Specific analyzer for degrees Celsius, specific info:
        - Values sub zero
    """
    calculations = []

    calculations.append(elements_sub_zero(data))

    return calculations

def unit_specific_analyzer(unitUri, data):
    print("getting unit")
    unit = get_unit_by_uri(unitUri)

    if (unit == "degrees_celsius"):
        return analyze_celsius(data)
    else:
        return None
