import re
import us
import geonamescache

gc = geonamescache.GeonamesCache()

us_cities = gc.get_cities()
us_states = us.states.mapping('abbr', 'name')
us_states_rev = us.states.mapping('name', 'abbr')

def find_city_state_in_title(title):
    title_cleaned = title.lower()

    

    detected_city = None
    detected_state = None
    try:
        for city in us_cities.values():
            city_name = city['name'].lower()
            #if re.search(rf'\b{re.escape(city_name)}\b', title_cleaned):
            if re.search(rf'\b{re.escape(city_name)}\b', title_cleaned):
    
                detected_city = city['name']
                
                break
    except:
        pass        
    try:
        for state_name in us_states.values():
            if re.search(rf'\b{re.escape(state_name.lower())}\b', title_cleaned):
                detected_state = state_name
                
                break
    except:
        pass

    try:    
        for abbr, name in us_states.items():
            if re.search(rf'\b{re.escape(abbr.lower())}\b', title_cleaned, re.IGNORECASE):
                detected_state = name
                
                break
    except:
        pass
    return detected_city, detected_state

def filter_job_title(job_title):
    sales_keywords = [
        "sales",
        "account manager",
        "sales specialist",
        "sales manager",
        "representative",
        "district",
        "specialist",
        "regional"
    ]
    for keyword in sales_keywords:
        if keyword.lower() in job_title.lower():
            return True
    return False
