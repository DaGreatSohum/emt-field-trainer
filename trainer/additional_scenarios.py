"""Ten additional protocol-grounded BLS field-training calls."""


def step(prompt, concepts, critical):
    return {
        "prompt": prompt,
        "concepts": concepts,
        "critical": critical,
        "first_hint": "Although that step might be important at another time, what should you consider now?",
        "partial_hint": "You identified {matched}. What else is important at this stage?",
    }


ADDITIONAL_SCENARIOS = {
    "chf": {
        "title": "CHF / Pulmonary Edema", "category": "Respiratory",
        "difficulty": "Advanced", "protocol": "Maryland 6.3-A",
        "dispatch": "74-year-old with severe shortness of breath, orthopnea, edema, and rales.",
        "steps": [
            step("The patient is tripod-positioned with rales and SpO2 88%. Assess and treat.",
                 {"upright position": ["upright", "high fowler", "position of comfort", "tripod"],
                  "ABCs/breathing severity": ["abc", "airway", "breathing", "respiratory distress", "work of breathing"],
                  "oxygen/SpO2": ["oxygen", "o2", "spo2", "pulse ox"],
                  "ALS": ["als", "paramedic", "medic"]},
                 ["upright position", "ABCs/breathing severity", "oxygen/SpO2", "ALS"]),
            step("He becomes confused and can speak only one word at a time. What now?",
                 {"ventilatory support": ["bvm", "assist ventilation", "ventilate", "positive pressure"],
                  "rapid transport": ["rapid transport", "priority 1", "emergency transport"],
                  "reassessment": ["reassess", "monitor", "repeat vital"],
                  "ALS": ["als", "paramedic", "medic"]},
                 ["ventilatory support", "rapid transport", "ALS"]),
        ],
    },
    "pediatric_asthma": {
        "title": "Pediatric Respiratory Distress", "category": "Pediatrics",
        "difficulty": "Advanced", "protocol": "Maryland 6.1-P + 6.5",
        "dispatch": "Seven-year-old with wheezing, retractions, and worsening breathing.",
        "steps": [
            step("The child is alert but retracting and wheezing. What is your assessment and care?",
                 {"pediatric assessment triangle": ["pediatric assessment triangle", "pat", "appearance circulation breathing"],
                  "ABCs/SpO2": ["abc", "airway", "breathing", "spo2", "pulse ox"],
                  "albuterol": ["albuterol", "nebulizer", "bronchodilator"],
                  "oxygen": ["oxygen", "o2"], "ALS": ["als", "paramedic"]},
                 ["pediatric assessment triangle", "ABCs/SpO2", "albuterol", "ALS"]),
            step("Air movement declines and the child becomes drowsy. What now?",
                 {"BVM ventilation": ["bvm", "bag valve", "assist ventilation", "ventilate"],
                  "rapid transport": ["rapid transport", "priority 1", "emergency transport"],
                  "ALS": ["als", "paramedic"], "reassessment": ["reassess", "monitor"]},
                 ["BVM ventilation", "rapid transport", "ALS"]),
        ],
    },
    "syncope": {
        "title": "Syncope", "category": "Medical", "difficulty": "Intermediate",
        "protocol": "Maryland 4.18", "dispatch": "68-year-old briefly fainted while standing.",
        "steps": [
            step("The patient is now awake on the floor. What should you assess first?",
                 {"ABCs": ["abc", "airway", "breathing", "circulation"],
                  "supine position": ["supine", "lay flat", "feet elevated"],
                  "glucose": ["glucose", "blood sugar", "bgl"],
                  "stroke/trauma assessment": ["stroke", "neurologic", "trauma", "injury", "fall"]},
                 ["ABCs", "supine position", "glucose", "stroke/trauma assessment"]),
            step("Vitals are stable, but the cause remains unclear. What is your plan?",
                 {"history/vitals": ["sample", "history", "vital", "orthostatic"],
                  "cardiac monitoring": ["cardiac monitor", "12 lead", "ecg", "aed"],
                  "transport": ["transport", "hospital"], "reassessment": ["reassess", "monitor"]},
                 ["history/vitals", "transport", "reassessment"]),
        ],
    },
    "sepsis": {
        "title": "Suspected Sepsis", "category": "Medical", "difficulty": "Advanced",
        "protocol": "Maryland 4.15-A", "dispatch": "79-year-old with fever, weakness, and confusion.",
        "steps": [
            step("The patient is hot, tachycardic, tachypneic, and confused. What do you assess?",
                 {"ABCs": ["abc", "airway", "breathing", "circulation"],
                  "infection source": ["infection", "fever", "source", "sepsis"],
                  "sepsis criteria/vitals": ["sepsis criteria", "temperature", "heart rate", "respiratory rate", "blood pressure", "vital"],
                  "glucose": ["glucose", "blood sugar", "bgl"]},
                 ["ABCs", "infection source", "sepsis criteria/vitals"]),
            step("BP is 82/48 with persistent altered mental status. What is your plan?",
                 {"shock care": ["shock", "supine", "keep warm", "perfusion"],
                  "priority 1 transport": ["priority 1", "p1", "rapid transport", "emergency transport"],
                  "sepsis notification": ["sepsis alert", "sepsis notification", "notify hospital"],
                  "ALS": ["als", "paramedic"]},
                 ["shock care", "priority 1 transport", "sepsis notification", "ALS"]),
        ],
    },
    "heat_emergency": {
        "title": "Heat Emergency", "category": "Environmental", "difficulty": "Intermediate",
        "protocol": "Maryland 7.5", "dispatch": "Runner collapsed on a hot, humid afternoon.",
        "steps": [
            step(
                "You approach the confused, very hot, sweaty patient. What do you evaluate immediately while forming your general impression?",
                {
                    "immediate life threats": ["life threat", "abc", "airway compromise", "respiratory distress", "poor perfusion"],
                    "critical instability": ["critically unstable", "unstable", "critical", "imminent deterioration"],
                    "general impression": ["general impression", "overall appearance", "looks sick", "patient appearance"],
                },
                ["immediate life threats"],
            ),
            step(
                "You see no immediately correctable life threat. What should you assess next as you introduce yourself?",
                {
                    "mental status/AVPU": ["mental status", "avpu", "alert", "verbal", "pain", "unresponsive", "orientation"],
                    "professional introduction": ["introduce", "emt", "ems", "fire department", "how can i help", "what is the problem"],
                },
                ["mental status/AVPU"],
            ),
            step(
                "The patient opens his eyes to your voice but answers incoherently. What part of the initial assessment comes next?",
                {
                    "airway": ["airway", "patent"],
                    "breathing": ["breathing", "respiratory rate", "respirations", "chest rise"],
                    "circulation": ["circulation", "pulse", "perfusion", "skin", "major bleeding"],
                    "ABCs": [
                        "abc", "airway breathing circulation",
                        "primary assessment", "initial assessment",
                    ],
                },
                ["ABCs"],
            ) | {
                "context_hints": [
                    {
                        "aliases": [
                            "aox4", "ao x4", "alert and oriented", "orientation",
                            "person place time situation", "person place time event",
                        ],
                        "feedback": (
                            "A&O x4 is useful for the focused neurologic assessment once "
                            "immediate threats are addressed. Because the patient is altered, "
                            "continue the initial assessment now: what comes after mental status?"
                        ),
                    }
                ]
            },
            step(
                "The airway is patent, breathing is rapid but adequate, the pulse is rapid, and no major bleeding is present. What is the final initial-assessment decision?",
                {
                    "assign clinical priority": [
                        "clinical priority", "assign priority", "transport priority",
                        "priority 1", "priority one", "p1",
                    ],
                    "Priority 1": ["priority 1", "priority one", "p1", "critically unstable"],
                },
                ["assign clinical priority", "Priority 1"],
            ) | {
                "context_hints": [
                    {
                        "aliases": ["p2", "priority 2", "priority two"],
                        "feedback": (
                            "Priority 2 is not appropriate here. Persistent altered mental "
                            "status with suspected heat stroke makes this patient critically "
                            "unstable. What clinical priority should you assign?"
                        ),
                    }
                ]
            },
            step(
                "Now perform the focused heat-emergency assessment. What findings and immediate environmental actions matter?",
                {
                    "temperature": ["temperature", "temp", "core temperature"],
                    "heat exposure/history": ["heat exposure", "hot environment", "exertion", "exercise", "history", "how long"],
                    "remove from heat": [
                        "remove from heat", "cool environment", "cooler place",
                        "move to cooler", "moving to cooler", "get out of heat",
                        "shade", "air conditioning", "cool ambulance",
                    ],
                    "remove excess clothing": [
                        "remove clothing", "remove excess clothing", "loosen clothing",
                        "excess clothing", "take off clothing",
                        "take off excessive clothing", "strip clothing",
                    ],
                    "heat stroke": ["heat stroke", "altered mental", "confused", "hyperthermia"],
                },
                ["temperature", "heat exposure/history", "remove from heat"],
            ) | {
                "context_hints": [
                    {
                        "aliases": [
                            "aggressive cooling", "cooling packs", "cool packs",
                            "ice packs", "wet sheets", "mist and fan",
                        ],
                        "feedback": (
                            "Active cooling is appropriate treatment once the focused "
                            "heat assessment is completed. What temperature, exposure "
                            "history, and immediate environmental actions do you assess now?"
                        ),
                    }
                ]
            },
            step(
                "The temperature is markedly elevated and altered mental status persists. What treatment and transport plan do you initiate?",
                {
                    "aggressive cooling": ["aggressive cooling", "cool packs", "ice packs", "wet sheet", "wet towel", "mist", "fan"],
                    "rapid transport": [
                        "rapid transport", "priority 1", "emergency transport",
                        "transport", "hospital", "go to hospital", "transport to hospital",
                        "load and go",
                    ],
                    "ALS": ["als", "paramedic"],
                    "reassessment": [
                        "reassess", "reassessment", "monitor",
                        "repeat temperature", "repeat vital",
                    ],
                },
                ["aggressive cooling", "rapid transport", "ALS", "reassessment"],
            ),
        ],
    },
    "carbon_monoxide": {
        "title": "Carbon Monoxide Exposure", "category": "Environmental",
        "difficulty": "Advanced", "protocol": "Maryland 7.1",
        "dispatch": "Several occupants report headache and nausea near a running generator.",
        "steps": [
            step("What are your immediate actions on arrival?",
                 {"scene safety/removal": ["scene safety", "do not enter", "remove from exposure", "fresh air"],
                  "multiple patients/resources": ["multiple patient", "patient count", "fire department", "hazmat", "additional resource"],
                  "high-flow oxygen": ["high flow oxygen", "100 percent oxygen", "nonrebreather", "nrb"],
                  "ABCs": ["abc", "airway", "breathing", "circulation"]},
                 ["scene safety/removal", "multiple patients/resources", "high-flow oxygen", "ABCs"]),
            step("The patient's standard pulse oximeter reads 99%, but headache and confusion persist. What now?",
                 {"pulse ox limitation": ["pulse ox unreliable", "spo2 unreliable", "normal pulse ox", "co oximeter"],
                  "continued oxygen": ["continue oxygen", "high flow oxygen", "100 percent oxygen"],
                  "transport/destination": ["transport", "hyperbaric", "appropriate hospital"],
                  "reassessment": ["reassess", "monitor"]},
                 ["pulse ox limitation", "continued oxygen", "transport/destination"]),
        ],
    },
    "submersion": {
        "title": "Submersion Injury", "category": "Environmental", "difficulty": "Advanced",
        "protocol": "Maryland 7.10", "dispatch": "Teen removed from cold water after a witnessed submersion.",
        "steps": [
            step("Rescuers have brought the patient to shore. What is your approach?",
                 {"rescuer safety": ["rescuer safety", "water rescue", "safe removal", "scene safety"],
                  "ABCs": ["abc", "airway", "breathing", "circulation"],
                  "hypothermia": ["hypothermia", "keep warm", "remove wet clothing"],
                  "submersion history": ["submersion time", "time underwater", "water temperature"]},
                 ["rescuer safety", "ABCs", "hypothermia"]),
            step("The patient is coughing, dyspneic, and SpO2 is 90%. What now?",
                 {"oxygen/ventilation": ["oxygen", "o2", "bvm", "assist ventilation"],
                  "ALS": ["als", "paramedic"], "rapid transport": ["rapid transport", "transport"],
                  "reassessment": ["reassess", "monitor", "spo2"]},
                 ["oxygen/ventilation", "ALS", "rapid transport"]),
        ],
    },
    "spinal_injury": {
        "title": "Spinal Motion Restriction", "category": "Trauma",
        "difficulty": "Advanced", "protocol": "Maryland 8.6-A",
        "dispatch": "Adult fell down stairs and reports neck pain and arm tingling.",
        "steps": [
            step("How do you assess and initially manage this patient?",
                 {"manual stabilization": ["manual stabilization", "inline stabilization", "hold c spine", "cervical spine"],
                  "neurologic/SMR criteria": ["neurologic", "numbness", "tingling", "midline", "neck pain", "smr criteria"],
                  "ABCs": ["abc", "airway", "breathing", "circulation"],
                  "cervical collar": ["cervical collar", "c collar", "collar"]},
                 ["manual stabilization", "neurologic/SMR criteria", "ABCs", "cervical collar"]),
            step("He has midline tenderness and persistent arm tingling. How will you move and monitor him?",
                 {"minimize movement": ["minimize movement", "spinal motion restriction", "smr", "scoop", "backboard"],
                  "PMS before/after": ["pms", "pulse motor sensation", "neuro before", "neuro after"],
                  "transport": ["transport", "trauma center"], "reassessment": ["reassess", "monitor"]},
                 ["minimize movement", "PMS before/after", "transport"]),
        ],
    },
    "agitation": {
        "title": "Behavioral Emergency / Agitation", "category": "Behavioral",
        "difficulty": "Advanced", "protocol": "Maryland 4.2-A",
        "dispatch": "Agitated adult pacing and shouting after an unknown substance exposure.",
        "steps": [
            step("What are your first patient-contact priorities?",
                 {"scene safety/law enforcement": ["scene safety", "law enforcement", "police", "escape route"],
                  "verbal de-escalation": ["deescalation", "de escalate", "calm", "rapport", "safer"],
                  "medical causes/capacity": ["medical cause", "capacity", "suicide", "self harm", "substance", "trauma"],
                  "ABCs": ["abc", "airway", "breathing", "circulation"]},
                 ["scene safety/law enforcement", "verbal de-escalation", "medical causes/capacity"]),
            step("The patient agrees to evaluation but remains restless. How do you continue safely?",
                 {"non-prone positioning": ["supine", "position of comfort", "not prone", "non prone", "avoid prone"],
                  "monitor causes": ["glucose", "temperature", "trauma", "vital", "monitor"],
                  "transport": ["transport", "hospital"], "ALS": ["als", "paramedic"]},
                 ["non-prone positioning", "monitor causes", "transport"]),
        ],
    },
    "childbirth": {
        "title": "Imminent Childbirth", "category": "Obstetrics",
        "difficulty": "Advanced", "protocol": "Maryland 5.1",
        "dispatch": "Term pregnant patient with contractions two minutes apart and urge to push.",
        "steps": [
            step("What determines whether you deliver here or transport now?",
                 {"ABCs": ["abc", "airway", "breathing", "circulation"],
                  "imminent delivery assessment": ["crowning", "urge to push", "contraction", "delivery imminent"],
                  "bleeding/ob history": ["bleeding", "gravida", "para", "due date", "pregnancy history"],
                  "OB kit/PPE": ["ob kit", "delivery kit", "ppe", "gloves"]},
                 ["ABCs", "imminent delivery assessment", "bleeding/ob history", "OB kit/PPE"]),
            step("Crowning is present and the head delivers. Describe your care.",
                 {"support head/body": ["support head", "support baby", "control delivery", "gentle"],
                  "nuchal cord": ["nuchal cord", "cord around neck"],
                  "newborn ABCs/warmth": ["newborn", "dry", "warm", "stimulate", "breathing", "airway"],
                  "mother/placenta/transport": ["placenta", "mother", "bleeding", "transport"]},
                 ["support head/body", "nuchal cord", "newborn ABCs/warmth", "mother/placenta/transport"]),
        ],
    },
}
