import requests
import csv


def main():
    # https://clinicaltrials.gov/data-api/api
    API_SERVER = "https://clinicaltrials.gov/api/v2"
    cond = 'FHA'

    # curl -X GET "https://clinicaltrials.gov/api/v2/studies?query.cond=FHA" -H "accept: application/json"
    get_by_cond_endpoint = f"{API_SERVER}/studies?query.cond={cond}"

    resp_cond = requests.get(get_by_cond_endpoint)

    if resp_cond.status_code == 200:

        data = resp_cond.json()
        # identificationModule: { nctId: string ... }
        # e.g 'eligibilityModule': {
        # 'eligibilityCriteria': 'Main Inclusion Criteria:\n\n* Male and female patients, aged 18 and above.\n* ApoA-I \\< 70 mg/dL\n* Symptomatic or asymptomatic cardiovascular disease\n* Diagnosis of genetically confirmed HDL-c deficiency due to defects in genes coding for ABCA1 and/or ApoA-1\n* Stable doses of lipid lowering therapies for at least 6 weeks prior to baseline procedures\n\nMain Exclusion Criteria:\n\n* Females of childbearing potential\n* Patients with LCAT mutations\n* Patients who experienced recent cardiovascular or cerebrovascular events\n* Hypertriglyceridemia (\\>500 mg/dL)\n* Severe anemia (Hgb \\< 10 g/dL)\n* Uncontrolled diabetes (HbA1c \\>10%)\n* Congestive heart failure (NYHA class II or higher)\n* Contraindication for MRI scanning (e.g., implanted metal objects, claustrophobia)',

        # Initialize lists for OMOP format data
        eligibility_criteria = []
        # print('study',  data.get("studies")[0])
        for study_p in data.get("studies"):
            study = study_p.get('protocolSection')
            nctId = study.get("identificationModule", {}).get("nctId")
            eligibilityModule = study.get("eligibilityModule", {})
            # eligibilityCriteria: string
            # healthyVolunteers: boolean
            # sex: enum
            # genderBased: boolean
            # genderDescription: string
            # minimumAge: string
            # maximumAge: string
            # stdAges: [enum]
            # studyPopulation: string
            # samplingMethod: enum

            if eligibilityModule:
                eligibilityCriteria = eligibilityModule.get("eligibilityCriteria", {})  # str
                healthyVolunteers = eligibilityModule.get("healthyVolunteers")  # bool
                sex = eligibilityModule.get("sex")  # enum
                genderBased = eligibilityModule.get("genderBased")
                minimumAge = eligibilityModule.get("minimumAge")
                maximumAge = eligibilityModule.get("maximumAge")
                stdAges = eligibilityModule.get("stdAges")
                studyPopulation = eligibilityModule.get("studyPopulation")
                samplingMethod = eligibilityModule.get("samplingMethod")

                data_col_row = {
                    "nctId": nctId,
                    "eligibilityCriteria": eligibilityCriteria,
                    "healthyVolunteers": healthyVolunteers,
                    "sex": sex,
                    "genderBased": genderBased,
                    "minimumAge": minimumAge,
                    "maximumAge": maximumAge,
                    "stdAges": stdAges,
                    "studyPopulation": studyPopulation,
                    "samplingMethod": samplingMethod}

                eligibility_criteria.append(data_col_row)

        # save data to csv
        with open(f'{cond}_trials_eligibility_criteria.csv', mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=["nctId", "eligibilityCriteria", "healthyVolunteers",
                                                      "sex", "genderBased", "minimumAge", "maximumAge", "stdAges",
                                                      "studyPopulation", "samplingMethod"])
            writer.writeheader()
            writer.writerows(eligibility_criteria)

        print("Data has been successfully written to 'observation_period.csv' and 'condition_occurrence.csv'.")

    else:
        # Print an error message if the request was not successful
        print(f"Error fetching data from {get_by_cond_endpoint}: {resp_cond.status_code}")
        print(resp_cond.text)


if __name__ == '__main__':
    main()
