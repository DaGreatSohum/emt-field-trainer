from copy import deepcopy


EQUIPMENT_RESPONSE_INTRO = (
    "Thanks for your response. Although the 2026 Maryland EMS Protocol do not "
    "prescribe equipment for calls, a recommended extensive equipment list is below:"
)

EQUIPMENT_STEP = {
    "prompt": (
        "You have a three-person BLS crew: you, your ambulance driver, and your "
        "partner. What equipment do you plan on bringing to the scene?"
    ),
    "concepts": {},
    "critical": [],
    "graded": False,
    "advance_always": True,
}

EQUIPMENT_LISTS = {
    "chest_pain": [
        "Primary bag (Jump bag, Green bag) with vital-sign equipment",
        "Oxygen and airway equipment, including BVM and suction",
        "AED/cardiac monitor and authorized BLS medications",
        "Cot",
        "Stair chair",
    ],
    "breathing": [
        "Primary bag (Jump bag, Green bag) with pulse oximeter and stethoscope",
        "Oxygen and airway equipment, including BVM, adjuncts, and suction",
        "Nebulizer/inhaler supplies and authorized respiratory medications",
        "AED/cardiac monitor",
        "Cot",
        "Stair chair",
    ],
    "anaphylaxis": [
        "Primary bag (Jump bag, Green bag) with vital-sign equipment",
        "Oxygen and airway equipment, including BVM and suction",
        "Authorized epinephrine and bronchodilator equipment",
        "AED/cardiac monitor",
        "Cot",
        "Stair chair",
    ],
    "hypoglycemia": [
        "Primary bag (Jump bag, Green bag)",
        "Glucometer and blood-glucose testing supplies",
        "Oral glucose and other authorized hypoglycemia treatment supplies",
        "Oxygen and airway equipment, including BVM and suction",
        "Cot",
        "Stair chair",
    ],
    "seizure": [
        "Primary bag (Jump bag, Green bag)",
        "Oxygen and airway equipment, including BVM, adjuncts, and suction",
        "Glucometer and blood-glucose testing supplies",
        "AED/cardiac monitor",
        "Cot with equipment to protect the patient from injury",
        "Stair chair when appropriate after seizure activity stops",
    ],
    "stroke": [
        "Primary bag (Jump bag, Green bag) with vital-sign equipment",
        "Glucometer and blood-glucose testing supplies",
        "Oxygen and airway equipment, including BVM and suction",
        "AED/cardiac monitor",
        "Cot",
        "Stair chair",
    ],
    "overdose": [
        "Appropriate PPE and the primary bag (Jump bag, Green bag)",
        "Oxygen and airway equipment, including BVM, adjuncts, and suction",
        "Authorized naloxone",
        "AED/cardiac monitor",
        "Cot",
        "Stair chair",
    ],
    "burns": [
        "Appropriate PPE and the primary bag (Jump bag, Green bag)",
        "Oxygen and airway equipment, including BVM and suction",
        "Clean dry sheets or a Mylar blanket and burn-care supplies",
        "Trauma and hemorrhage-control supplies",
        "Cot",
        "Stair chair only when clinically and operationally appropriate",
    ],
    "major_trauma": [
        "Appropriate PPE and trauma/primary bags",
        "Hemorrhage-control supplies, including tourniquets and wound-packing materials",
        "Oxygen and airway equipment, including BVM, adjuncts, suction, and chest seals",
        "Spinal-motion-restriction and pelvic-stabilization equipment when indicated",
        "AED/cardiac monitor",
        "Cot and appropriate extrication/movement equipment",
    ],
    "cardiac_arrest": [
        "Appropriate PPE",
        "AED/defibrillator",
        "Oxygen and airway equipment, including BVM, adjuncts, and suction",
        "Primary bag (Jump bag, Green bag)",
        "CPR movement equipment or mechanical CPR device if available and indicated",
        "Cot",
    ],
    "chf": ["Primary bag with vital-sign and pulse-oximetry equipment", "Oxygen, suction, airway adjuncts, and BVM", "AED/cardiac monitor and CPAP equipment when available within scope", "Cot", "Stair chair"],
    "pediatric_asthma": ["Pediatric primary/airway bag", "Oxygen, suction, and pediatric BVM", "Nebulizer and authorized pediatric respiratory medications", "AED/cardiac monitor", "Cot"],
    "syncope": ["Primary bag with vital-sign equipment", "Glucometer", "Oxygen, airway equipment, BVM, and suction", "AED/cardiac monitor", "Cot and stair chair"],
    "sepsis": ["Appropriate PPE and primary bag with thermometer and vital-sign equipment", "Glucometer", "Oxygen, airway equipment, BVM, and suction", "AED/cardiac monitor", "Cot"],
    "heat_emergency": ["Primary bag with thermometer and vital-sign equipment", "Cooling supplies: cool packs, wet sheets/towels, water mist, and fan", "Oxygen and airway equipment", "AED/cardiac monitor", "Cot"],
    "carbon_monoxide": ["Appropriate PPE; fire/hazmat and atmospheric-monitoring resources", "High-concentration oxygen, airway equipment, and BVM", "CO-oximeter when available", "AED/cardiac monitor", "Cot"],
    "submersion": ["Water-rescue PPE and trained rescue resources", "Oxygen, suction, airway adjuncts, and BVM", "Warming blankets and dry coverings", "AED/cardiac monitor", "Cot and appropriate movement equipment"],
    "spinal_injury": ["Trauma/primary bag", "Cervical collars and spinal-motion-restriction movement equipment", "Oxygen, suction, airway adjuncts, and BVM", "Hemorrhage-control supplies", "Cot"],
    "agitation": ["Appropriate PPE, primary bag, and law-enforcement support when needed", "Oxygen, suction, airway equipment, and BVM", "Glucometer, thermometer, and vital-sign equipment", "AED/cardiac monitor", "Authorized restraint equipment and cot"],
    "childbirth": ["Obstetric delivery kit and appropriate PPE", "Oxygen, suction, adult and neonatal airway equipment/BVMs", "Newborn drying and warming supplies", "Neonatal resuscitation supplies", "Cot"],
}

PATIENT_DEMOGRAPHICS = {
    "chest_pain": "62-year-old male",
    "breathing": "53-year-old female",
    "anaphylaxis": "34-year-old female",
    "hypoglycemia": "58-year-old male",
    "seizure": "27-year-old female",
    "stroke": "71-year-old female",
    "overdose": "approximately 30-year-old male",
    "burns": "42-year-old female",
    "major_trauma": "36-year-old male",
    "cardiac_arrest": "55-year-old male",
    "chf": "74-year-old female",
    "pediatric_asthma": "7-year-old male",
    "syncope": "68-year-old female",
    "sepsis": "79-year-old male",
    "heat_emergency": "approximately 25-year-old male",
    "carbon_monoxide": "45-year-old female index patient; additional patients unknown",
    "submersion": "16-year-old male",
    "spinal_injury": "40-year-old female",
    "agitation": "approximately 32-year-old male",
    "childbirth": "28-year-old female",
}


def equipment_response(scenario_key):
    items = "\n".join(f"- {item}" for item in EQUIPMENT_LISTS[scenario_key])
    return f"{EQUIPMENT_RESPONSE_INTRO}\n{items}"

SCENE_SIZEUP_STEP = {
    "prompt": "You arrive on scene. What are your first considerations?",
    "concepts": {
        "Scene Arrival and Size-Up": [
            "scene size up", "scene sizeup", "size up", "sizeup",
            "scene arrival and size up",
        ],
        "BSI/PPE": ["bsi", "ppe", "gloves", "body substance", "proper protection"],
        "scene safety": [
            "scene safe", "scene safety", "is the scene safe", "is it safe",
            "hazard", "safe scene",
        ],
        "number of patients": [
            "number of patient", "number of pts", "how many patient", "how many pts",
            "one patient", "1 patient", "only patient", "only pt", "any other patient",
            "one child", "only child", "one mother", "only mother", "any other pts",
            "more patient", "additional patient", "count patient",
            "patient count",
        ],
        "additional resources": [
            "additional resource", "additional unit", "more unit", "als", "engine",
            "paramedic", "fire department", "request resource", "request unit",
            "no additional resource", "no additional unit", "do not need more unit",
            "extra resource", "extra unit", "more resources",
            "medic unit", "upgrade response", "upgrade with medic",
            "hazmat", "fire rescue", "rescue squad",
        ],
    },
    "critical": ["BSI/PPE", "scene safety", "number of patients", "additional resources"],
    "first_hint": "Although that step might be important at another time, what should you consider now?",
    "second_hint": (
        "Although that step might be important at another time, conduct the Scene "
        "Arrival and Size-Up first. What belongs in that assessment?"
    ),
    "partial_hint": "You identified {matched}. What else is important for the Scene Size-Up?",
    "context_hints": [
        {
            "aliases": [
                "life threat", "general impression", "avpu", "mental status",
                "airway", "breathing", "circulation",
            ],
            "feedback": (
                "Assessing life threats and the patient is important immediately after "
                "Scene Arrival and Size-Up. Before approaching, what scene considerations "
                "must you complete?"
            ),
        }
    ],
    "completion": (
        "Under Maryland GPC 2.1, Scene Arrival and Size-Up includes considering BSI, "
        "selecting appropriate PPE, evaluating scene safety, determining the number of "
        "patients, and considering the need for additional resources.\n\nDetermining "
        "NOI versus MOI is the next Patient Approach step, immediately after scene "
        "size-up. Cervical-spine stabilization is considered later during the Airway "
        "portion of the initial assessment when appropriate; it is not automatically "
        "required on every call."
    ),
    "resource_context": True,
}

ORIENTATION_STEP = {
    "prompt": (
        "The patient is responsive enough to answer questions. As part of the focused "
        "neurologic and mental-status assessment, how will you evaluate orientation?"
    ),
    "concepts": {
        "orientation/A&O x4": [
            "aox4", "ao x4", "a o x4", "a and o x4", "alert and oriented x4",
            "oriented times 4", "orientation", "oriented",
        ],
        "person, place, time, and situation/event": [
            "person place time situation", "person place time event",
            "person place time events", "name place time event",
            "name place time events", "name place time situation",
            "name location date what happened", "who where when what happened",
            "aox4", "ao x4", "alert and oriented x4", "oriented times 4",
        ],
    },
    "critical": ["orientation/A&O x4", "person, place, time, and situation/event"],
    "first_hint": (
        "AVPU establishes level of responsiveness. For a responsive patient with a "
        "possible neurologic or mental-status problem, what four orientation domains "
        "can you assess?"
    ),
    "partial_hint": "You identified {matched}. What else completes the orientation assessment?",
    "completion": (
        "Assess orientation to person, place, time, and situation/event (often documented "
        "as A&O x4). Record the patient's actual answers rather than only the shorthand. "
        "Maryland GPC uses AVPU for the initial mental-status check; this more detailed "
        "orientation assessment supports the focused neurologic examination. It is also "
        "explicitly required when evaluating decision-making capability for a refusal."
    ),
}

# Position is within the clinical-step list, after time-critical ABC work.
ORIENTATION_INSERTIONS = {
    "hypoglycemia": 1,
    "seizure": 1,
    "stroke": 1,
    "syncope": 1,
    "sepsis": 1,
    "heat_emergency": 3,
    "carbon_monoxide": 1,
    "spinal_injury": 1,
    "agitation": 1,
}

TRANSPORT_CLOSURE_STEP = {
    "prompt": (
        "The patient has been packaged and transport has begun. What ongoing care "
        "should continue during transport?"
    ),
    "concepts": {
        "ongoing reassessment": [
            "reassess", "reassessment", "repeat abc", "repeat vital",
            "trend vital", "monitor patient",
        ],
        "continue indicated care": [
            "continue treatment", "continue care", "monitor intervention",
            "response to treatment", "treatment effectiveness",
        ],
    },
    "critical": ["ongoing reassessment", "continue indicated care"],
    "required": ["ongoing reassessment"],
    "first_hint": "Patient care continues during transport. What must be repeated and monitored?",
    "partial_hint": "You identified {matched}. What else must continue during transport?",
    "completion": (
        "During transport, continue indicated treatment and reassess mental status, "
        "ABCs, vital-sign trends, the chief complaint, and response to interventions. "
        "Repeat assessments sooner whenever the condition changes or after an intervention."
    ),
}

HOSPITAL_NOTIFICATION_STEP = {
    "prompt": (
        "Before arrival, what notification should you give the receiving hospital, "
        "and what information belongs in it?"
    ),
    "concepts": {
        "hospital notification": [
            "hospital notification", "notify hospital", "prearrival notification",
            "radio report", "call hospital", "emrc", "hospital report",
            "eta", "chief complaint", "cc", "minutes out",
        ],
        "patient/complaint/priority": [
            "age complaint priority", "age sex complaint", "patient information",
            "chief complaint", "clinical priority", "cc", "year old", "y o",
            "male", "female", "heat stroke",
        ],
        "ETA": ["eta", "estimated time", "minutes out", "time of arrival"],
        "vitals/treatments/response": [
            "vital treatment response", "vitals and treatment", "intervention response",
            "assessment treatment", "trending vital",
        ],
    },
    "critical": ["hospital notification", "patient/complaint/priority", "ETA"],
    "required": ["hospital notification"],
    "first_hint": "The receiving facility needs a prearrival report. How will you notify it?",
    "partial_hint": "You identified {matched}. What other essential notification information is missing?",
    "completion": (
        "Provide the required prearrival hospital notification through the appropriate "
        "communications channel. Include patient age/sex, chief complaint, assigned "
        "clinical priority, ETA, and pertinent assessment findings, vital-sign trends, "
        "treatments, and response."
    ),
}

TRANSFER_CLOSURE_STEP = {
    "prompt": (
        "You arrive at the receiving facility. What must occur before EMS responsibility "
        "for the patient ends?"
    ),
    "concepts": {
        "verbal handoff": [
            "verbal handoff", "give report", "handoff", "report to nurse",
            "report to clinician", "transfer care", "transfer of care",
        ],
        "transfer to receiving clinician": [
            "transfer care", "receiving clinician", "receiving nurse",
            "accepts care", "assumes responsibility",
        ],
        "assessment/treatment/trends": [
            "assessment treatment trend", "history assessment", "vital trend",
            "treatments and response", "patient report",
        ],
    },
    "critical": [
        "verbal handoff", "transfer to receiving clinician",
        "assessment/treatment/trends",
    ],
    "required": ["verbal handoff"],
    "first_hint": "A receiving clinician must formally assume responsibility. What should you do?",
    "partial_hint": "You identified {matched}. What else completes a safe transfer of care?",
    "completion": (
        "Give an organized verbal handoff to the receiving nurse or clinician and ensure "
        "that clinician assumes responsibility. Include pertinent history and assessment, "
        "initial and trending vital signs, treatments and doses, response, reassessments, "
        "and significant events. The incident does not end merely because transport or "
        "treatment was initiated."
    ),
}

DOCUMENTATION_CLOSURE_STEP = {
    "prompt": "After transfer of care, what remains before the call is complete?",
    "concepts": {
        "PCR/ePCR documentation": [
            "pcr", "epcr", "patient care report", "emeds", "document",
            "documentation", "chart",
        ],
        "accurate narrative/submission": [
            "narrative", "submit report", "submit documentation", "hospital copy",
            "complete report", "chart narrative",
        ],
    },
    "critical": ["PCR/ePCR documentation"],
    "first_hint": "Transfer is complete, but the encounter still requires a formal record. What is it?",
    "partial_hint": "You identified {matched}. What else completes the documentation process?",
    "completion": (
        "Complete the PCR/ePCR in eMEDS according to jurisdictional procedure. Accurately "
        "document dispatch, assessments, care, reassessments, transport, hospital "
        "notification, and transfer of care, then submit the required record."
    ),
}

ARREST_TRANSPORT_CLOSURE_STEP = deepcopy(TRANSPORT_CLOSURE_STEP)
ARREST_TRANSPORT_CLOSURE_STEP["prompt"] = (
    "ROSC is achieved and transport begins under the applicable cardiac-arrest protocol. "
    "What ongoing care should continue during transport?"
)
ARREST_TRANSPORT_CLOSURE_STEP["completion"] = (
    "After ROSC, continuously reassess airway, ventilation, circulation, mental status, "
    "vital signs, rhythm/AED readiness, and response to care during protocol-appropriate "
    "transport. Continue post-ROSC care within scope and obtain ALS support."
)


CLINICAL_COMPLETIONS = {
    "chf": [
        "Place the patient upright, assess ABCs and respiratory severity, obtain SpO2, provide oxygen as indicated, request ALS, and prepare for ventilatory support. CPAP is used only when authorized for the clinician/service and the patient meets protocol criteria.",
        "Confusion and one-word speech indicate respiratory failure. Support ventilation with BVM and oxygen as needed, request ALS, begin Priority 1 transport, and continuously reassess.",
    ],
    "pediatric_asthma": [
        "Use the Pediatric Assessment Triangle and ABCs, obtain SpO2, keep the child with a caregiver when practical, provide oxygen, administer authorized albuterol for wheezing, request ALS, and reassess.",
        "Drowsiness with declining air movement signals respiratory failure. Assist ventilation with an appropriately sized BVM and oxygen, obtain ALS, transport rapidly, and reassess continuously.",
    ],
    "syncope": [
        "Assess ABCs, position supine when tolerated, evaluate injuries from the fall, check glucose, and screen for neurologic/stroke findings and other causes.",
        "Obtain complete vitals and history, consider cardiac monitoring/12-lead through the appropriate clinician, transport for evaluation, and repeat ABCs, neurologic status, and vital signs.",
    ],
    "sepsis": [
        "Assess ABCs and identify suspected infection plus abnormal temperature, heart rate, respiratory rate, mental status, or blood pressure. Obtain full vital signs and glucose and look for shock.",
        "Hypotension with altered mental status is critically unstable. Provide shock care and airway support, request ALS, transport Priority 1, notify the hospital of suspected sepsis, and reassess frequently.",
    ],
    "heat_emergency": [
        "Rapidly form a general impression and look for immediate life threats and critical instability. Confusion in this setting is an early warning that the patient may be critically unstable.",
        "Introduce yourself while assessing mental status with AVPU. The patient responds to verbal stimulus but is confused, so mental status is abnormal.",
        "Continue the initial assessment through airway, breathing, and circulation. Here the airway is patent, breathing is rapid but adequate, the pulse is rapid, and no major external bleeding is present.",
        "Complete the initial assessment by assigning clinical priority. Persistent altered mental status with suspected heat stroke makes this patient critically unstable and Priority 1.",
        "Obtain temperature and heat-exposure/exertion history, move the patient into a cool environment, and remove excess clothing. Altered mental status with marked hyperthermia supports suspected heat stroke.",
        "Begin aggressive cooling with wet sheets/towels, mist and fan, and cool packs to the trunk as available without delaying Priority 1 transport. Request ALS and repeatedly reassess ABCs, mental status, vital signs, and temperature.",
    ],
    "carbon_monoxide": [
        "Do not enter an unsafe atmosphere. Use trained fire/hazmat resources, remove patients from exposure, account for multiple patients, assess ABCs, and give high-concentration oxygen.",
        "A standard pulse oximeter can appear normal in carbon-monoxide poisoning and does not rule it out. Continue high-concentration oxygen, monitor ABCs, and transport to an appropriate facility while considering protocol destination/hyperbaric criteria.",
    ],
    "submersion": [
        "Do not attempt an unsafe water rescue. Once removed by trained rescuers, assess ABCs, begin resuscitation when needed, prevent further heat loss, and obtain submersion time and water-temperature history.",
        "Treat hypoxia with oxygen and assist ventilation when inadequate, request ALS, transport promptly, and continuously reassess breathing, SpO2, circulation, temperature, and mental status.",
    ],
    "spinal_injury": [
        "Maintain manual in-line stabilization, assess ABCs, midline pain/tenderness, neurologic deficits, mental status, and distracting injury, and apply an appropriately sized cervical collar when indicated.",
        "Minimize spinal movement using the protocol-appropriate movement method, document pulse/motor/sensation before and after movement, transport to the appropriate facility, and reassess.",
    ],
    "agitation": [
        "Prioritize crew and patient safety, request law enforcement when indicated, preserve an exit route, use calm verbal de-escalation, and assess capacity, self-harm risk, trauma, substances, and medical causes.",
        "Continue medical assessment including ABCs, vitals, glucose, temperature, and trauma. Avoid prone restraint, monitor any restrained patient continuously, request ALS as needed, and transport.",
    ],
    "childbirth": [
        "Assess maternal ABCs, contractions, crowning/urge to push, bleeding, due date and obstetric history. Prepare PPE and the OB kit; do not delay an imminent delivery for transport.",
        "Support the head and body without pulling, check for a nuchal cord, dry/warm/stimulate and assess the newborn's ABCs, manage maternal bleeding and placenta appropriately, and transport mother and newborn.",
    ],
    "breathing": [
        (
            "Position the patient to support breathing and rapidly reassess airway, "
            "breathing adequacy, work of breathing, lung sounds, SpO2, and circulation. "
            "Administer oxygen when clinically indicated and give the authorized BLS "
            "bronchodilator for bronchospasm. Request ALS and keep the BVM and suction "
            "ready because two-word speech may indicate severe respiratory compromise."
        ),
        (
            "Declining mental status with poor air movement indicates failing ventilation. "
            "Open and maintain the airway, assist ventilations with a BVM and oxygen, request "
            "or rendezvous with ALS, begin high-priority transport, and continuously reassess "
            "ventilation, SpO2, pulse, and mental status."
        ),
    ],
    "anaphylaxis": [
        (
            "Treat this as anaphylaxis: assess and support ABCs, administer the authorized "
            "adult BLS epinephrine dose in the lateral thigh, provide oxygen as indicated, "
            "request ALS, remove the continuing exposure when safe, and transport promptly. "
            "For wheezing or bronchospasm, administer authorized albuterol."
        ),
        (
            "Persistent hypotension and wheezing require continued ABC support, shock care, "
            "prompt transport, frequent reassessment, and ALS care. Repeat epinephrine and "
            "additional medications only as authorized by the current Maryland protocol, "
            "local optional program, clinician level, and medical direction."
        ),
    ],
    "hypoglycemia": [
        (
            "Perform the initial assessment, check blood glucose early, obtain relevant "
            "diabetes/medication/meal history, and consider stroke or another cause of "
            "altered mental status. A glucose result is essential before attributing the "
            "presentation to hypoglycemia."
        ),
        (
            "Because the glucose is below 70 mg/dL and the patient can safely follow commands "
            "and swallow, give 10-15 grams of oral glucose between the gum and cheek. Protect "
            "the airway, reassess mental status and glucose, and repeat once after 10 minutes "
            "if not improved. Continue appropriate transport/refusal procedures."
        ),
    ],
    "seizure": [
        (
            "Do not restrain the patient or place anything in the mouth. Protect the patient "
            "from injury, time the seizure, manage the airway with suction/BVM readiness, "
            "administer oxygen when SpO2 is below 94% or cannot be obtained, check glucose, "
            "and request ALS for an ongoing seizure."
        ),
        (
            "After seizure activity stops, reassess ABCs and injuries, place the patient in "
            "an airway-protective position when appropriate, check glucose, obtain witness and "
            "seizure/medication history, monitor for recurrence, and transport."
        ),
    ],
    "stroke": [
        (
            "Support ABCs, determine last known well, perform the Cincinnati Prehospital "
            "Stroke Scale and LAMS as applicable, check glucose and treat hypoglycemia, and "
            "ask about anticoagulants and relevant history without delaying transport."
        ),
        (
            "Treat this as a time-sensitive stroke: begin rapid transport to the protocol-"
            "appropriate stroke destination, provide early stroke notification, continue "
            "ABCs and monitoring, and repeat neurologic findings and vital signs."
        ),
    ],
    "overdose": [
        (
            "Confirm scene safety and protect the crew from needles or substances. Assess "
            "responsiveness, airway, breathing, and pulse. Open and suction the airway as "
            "needed, begin BVM ventilation with oxygen for hypoventilation, apply an AED if "
            "the patient is pulseless, identify the substance when possible, and request ALS."
        ),
        (
            "With a pulse and respirations of four per minute, ventilation is the immediate "
            "priority: assist with BVM and oxygen. Administer authorized intranasal naloxone "
            "and titrate additional doses to a normal respiratory rate—not necessarily full "
            "consciousness. Transport and monitor for recurrent respiratory depression."
        ),
    ],
    "burns": [
        (
            "When safe, stop the burning process, remove wet clothing and jewelry, prevent "
            "hypothermia, assess airway and possible smoke inhalation, treat associated trauma, "
            "determine burn depth and BSA, and cover with a clean sheet or Mylar blanket. Do "
            "not apply ice or give anything by mouth."
        ),
        (
            "Facial involvement and 20% partial-thickness burns meet burn-center criteria. "
            "Provide high-concentration oxygen when smoke inhalation is suspected, remain "
            "prepared to manage the airway, prevent hypothermia, reassess, manage pain within "
            "scope, and transport promptly to the appropriate burn center."
        ),
    ],
    "major_trauma": [
        (
            "Ensure scene safety and PPE, assess mechanism and request needed rescue/ALS "
            "resources, control life-threatening hemorrhage immediately, and proceed through "
            "airway with cervical-spine motion restriction when indicated, breathing, and "
            "circulation. Do not delay critical interventions."
        ),
        (
            "Treat for hemorrhagic shock, prevent hypothermia, apply a pelvic stabilization "
            "binder when criteria are met, request ALS, minimize scene time, transport rapidly "
            "to the appropriate trauma center, and continuously reassess."
        ),
    ],
    "cardiac_arrest": [
        (
            "Confirm unresponsiveness, abnormal/absent breathing, and no pulse within 10 "
            "seconds. Begin high-quality uninterrupted compressions at 100-120/min, apply the "
            "AED as soon as available, provide appropriate BVM ventilations, assign team roles, "
            "and rotate compressors while minimizing interruptions."
        ),
        (
            "Clear the patient and deliver the advised shock, then immediately resume CPR for "
            "two minutes without a pulse check. Keep pauses at 10 seconds or less, continue "
            "ventilation and team rotation, request ALS, and follow the AED for the next rhythm "
            "analysis."
        ),
    ],
}


def standardize_scenarios(scenarios):
    """Apply the same ungraded preparation and GPC opening to every seeded call."""
    for key, scenario in scenarios.items():
        demographic = PATIENT_DEMOGRAPHICS[key]
        if "Patient information:" not in scenario["dispatch"]:
            scenario["dispatch"] += f"\nPatient information: {demographic}."
        if key == "chest_pain":
            scenario["steps"][0]["graded"] = False
            scenario["steps"][0]["advance_always"] = True
            scenario["steps"][0]["completion"] = equipment_response(key)
            continue

        clinical_steps = list(scenario["steps"])
        if clinical_steps and "equipment" in clinical_steps[0]["prompt"].lower():
            clinical_steps = clinical_steps[1:]

        completions = list(CLINICAL_COMPLETIONS[key])
        if key in ORIENTATION_INSERTIONS:
            position = ORIENTATION_INSERTIONS[key]
            clinical_steps.insert(position, deepcopy(ORIENTATION_STEP))
            completions.insert(position, ORIENTATION_STEP["completion"])
        if len(clinical_steps) != len(completions):
            raise ValueError(f"Completion count does not match scenario steps: {key}")
        for step, completion in zip(clinical_steps, completions):
            step["completion"] = completion
            step.setdefault(
                "first_hint",
                "Begin with the immediate assessment and care requested in this phase. "
                "What is your first priority?",
            )
            step.setdefault(
                "second_hint",
                "Review the findings in the prompt and the applicable protocol phase. "
                "Which required assessment or intervention comes next?",
            )
            step.setdefault(
                "partial_hint",
                "You identified {matched}. What other required action belongs in this phase?",
            )

        equipment_step = deepcopy(EQUIPMENT_STEP)
        equipment_step["completion"] = equipment_response(key)
        scenario["steps"] = [
            equipment_step,
            deepcopy(SCENE_SIZEUP_STEP),
            *clinical_steps,
            deepcopy(
                ARREST_TRANSPORT_CLOSURE_STEP
                if key == "cardiac_arrest"
                else TRANSPORT_CLOSURE_STEP
            ),
            deepcopy(HOSPITAL_NOTIFICATION_STEP),
            deepcopy(TRANSFER_CLOSURE_STEP),
            deepcopy(DOCUMENTATION_CLOSURE_STEP),
        ]
