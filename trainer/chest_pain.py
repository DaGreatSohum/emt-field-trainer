"""Complete Call 1 training script supplied by the project owner."""

CHEST_PAIN_SCENARIO = {
    "title": "Call 1: Chest Pain",
    "category": "Cardiac",
    "difficulty": "Intermediate",
    "protocol": "Maryland GPC 2.1 + Cardiac 3.9",
    "dispatch": (
        "You, the charge A2, are dispatched to 1234 Marias Street for chest pain. "
        "The CAD notes read: 62 Y/M CHEST PAIN."
    ),
    "steps": [
        {
            "prompt": (
                "You have a three-person BLS crew: you, your ambulance driver, and your "
                "partner. What equipment do you plan on bringing to the scene?"
            ),
            "concepts": {
                "primary bag": ["primary bag", "jump bag", "green bag", "medical bag"],
                "oxygen and airway equipment": ["oxygen", "o2", "airway", "bvm"],
                "cot": ["cot", "stretcher"],
                "stair chair": ["stair chair"],
            },
            "critical": ["primary bag", "oxygen and airway equipment"],
            "advance_always": True,
            "completion": (
                "Thanks for your response. Equipment selections are not graded in this "
                "training app. A recommended extensive equipment "
                "list includes:\n• Primary bag (jump bag/green bag)\n• Oxygen and airway "
                "equipment\n• Cot\n• Stair chair"
            ),
        },
        {
            "prompt": (
                "You arrive on scene at a two-story single-family home. "
                "What are your first considerations?"
            ),
            "concepts": {
                "Scene Arrival and Size-Up": [
                    "scene size up", "scene sizeup", "size up", "sizeup",
                    "scene arrival and size up",
                ],
                "BSI/PPE": ["bsi", "ppe", "gloves", "body substance"],
                "scene safety": ["scene safe", "scene safety", "hazard", "safe"],
                "number of patients": [
                    "number of patient",
                    "number of pts",
                    "how many patient",
                    "how many pts",
                    "one patient",
                    "1 patient",
                    "only patient",
                    "only pt",
                    "any other patient",
                    "any other pts",
                    "count patient",
                    "patient count",
                ],
                "additional resources": [
                    "additional resource", "extra resource", "more resources",
                    "als", "engine", "paramedic", "medic unit", "request resource",
                ],
            },
            "critical": ["BSI/PPE", "scene safety", "number of patients", "additional resources"],
            "first_hint": (
                "Although that step might be important at another time, what should you "
                "consider now?"
            ),
            "second_hint": (
                "Although that step might be important at another time, you want to "
                "conduct the Scene Size-Up first. What should you consider in the Scene Size-Up?"
            ),
            "partial_hint": "You identified {matched}. What else is important for the Scene Size-Up?",
            "completion": (
                "The complete scene size-up includes BSI/PPE, scene safety, number of "
                "patients, and consideration of additional resources.\n\nThe scene is safe, "
                "you have one patient, and gloves are appropriate.\n\nDetermining NOI "
                "versus MOI is the next step under Patient Approach, "
                "immediately after Scene Arrival and Size-Up. Cervical-spine stabilization "
                "is considered later during the Airway portion of the initial assessment "
                "when appropriate. Nothing in this atraumatic chest-pain presentation "
                "currently indicates a need for cervical-spine stabilization."
            ),
            "resource_context": True,
        },
        {
            "prompt": (
                "You approach the patient sitting on his couch. A nature of illness of "
                "chest pain is apparent. Assume there is no language barrier and no need "
                "for MCI procedures. You find a 62-year-old man sitting upright, clutching "
                "his chest, and appearing pale and sweaty. What is your response?"
            ),
            "concepts": {
                "general impression": [
                    "general impression", "appearance", "pale", "sweaty", "diaphoretic",
                    "life threat", "immediate threat", "critically unstable", "instability",
                ],
                "altered mental status": ["mental status", "altered", "avpu"],
                "airway compromise": ["airway", "airway compromise"],
                "acute respiratory distress": ["respiratory distress", "breathing", "dyspnea"],
                "poor perfusion": ["perfusion", "cyanosis", "circulation", "shock"],
            },
            "critical": ["general impression", "altered mental status", "airway compromise", "acute respiratory distress", "poor perfusion"],
            "minimum_matches": 1,
            "first_hint": "Although that step might be important at another time, what should you consider now?",
            "partial_hint": "You identified {matched}. What else belongs in the rapid general impression?",
            "completion": (
                "Assessing life threats and whether the patient is critically unstable "
                "happens while forming the general impression. This includes altered mental "
                "status, airway compromise, acute respiratory distress, and signs of poor "
                "perfusion such as cyanosis."
            ),
        },
        {
            "prompt": (
                "You observe no immediate life threats and determine the patient is not "
                "critically unstable. What is your response?"
            ),
            "concepts": {
                "mental status": ["mental status", "avpu", "alert"],
                "professional introduction": ["introduce", "hello", "fire department", "ems"],
                "chief complaint/airway": ["chief complaint", "issue today", "what is wrong", "airway"],
            },
            "critical": ["mental status"],
            "first_hint": "Although that step might be important at another time, what should you consider now?",
            "partial_hint": "You identified {matched}. How could you assess this naturally while speaking with the patient?",
            "completion": (
                "Assessing mental status is next. Saying, “Hello, I am with the Fire "
                "Department. What is the issue today?” professionally assesses alertness "
                "while learning the chief complaint and how patent the airway is."
            ),
        },
        {
            "prompt": (
                "The patient answers, “Ow... my chest hurts.” His answer is clear, loud, "
                "and understandable. Based on this, what can you conclude about his mental status?"
            ),
            "concepts": {
                "Alert on AVPU": ["alert", "avpu a", "a on avpu", "awake", "spontaneously"],
            },
            "critical": ["Alert on AVPU"],
            "first_hint": "Nice try, but that is not it. Try again.",
            "second_hint": "Use the AVPU scale. Which category fits a patient who spontaneously gives a clear response?",
            "completion": (
                "AVPU means Alert, responsive to Verbal stimuli, responsive to Pain, or "
                "Unresponsive. This patient is A: Alert, because he spontaneously replied. "
                "In the field, also observe whether he is awake and tracks you with his eyes."
            ),
        },
        {
            "prompt": (
                "After mental status, what three things should you look for, consider, and "
                "acknowledge before anything else? How will you assess them?"
            ),
            "concepts": {
                "airway patency": ["airway", "patent", "clear voice", "abc", "abcs"],
                "breathing rate/rhythm/quality": ["breathing", "respiratory", "chest rise", "rate", "rhythm", "quality", "abc", "abcs"],
                "SpO2": ["spo2", "pulse ox", "oxygen saturation"],
                "circulation/pulse": ["circulation", "pulse", "strength", "regularity", "abc", "abcs"],
                "skin/perfusion": ["skin", "color", "warmth", "perfusion"],
            },
            "critical": ["airway patency", "breathing rate/rhythm/quality", "circulation/pulse"],
            "first_hint": "Although that step might be important at another time, what should you consider now?",
            "second_hint": (
                "You should be thinking about the ABCs. What exactly about Airway, "
                "Breathing, and Circulation should you check for apparent life threats?"
            ),
            "partial_hint": "You identified {matched}. What else completes the ABC assessment?",
            "completion": (
                "A clear, loud voice confirms airway patency. Assess breathing rate, rhythm, "
                "and quality by observing chest rise and apply pulse oximetry. For circulation, "
                "assess pulse strength, speed, and regularity plus skin color and warmth. Here, "
                "the airway is patent, chest rise is regular, the pulse is regular, and the skin "
                "is pink, warm, and dry."
            ),
        },
        {
            "prompt": (
                "The initial or primary assessment is nearly over. "
                "What is its final step?"
            ),
            "concepts": {
                "assign clinical priority": ["priority", "clinical priority", "triage priority"],
                "Priority 2": ["priority 2", "priority two", "potentially life threatening"],
            },
            "critical": ["assign clinical priority", "Priority 2"],
            "first_hint": "Although that step might be important at another time, what should you consider now?",
            "second_hint": "Assign a clinical priority. What priority should this patient receive?",
            "partial_hint": "You identified {matched}. Which priority number fits this patient?",
            "completion": (
                "Assign a clinical priority. Priority 1 is critically unstable; Priority 2 "
                "is a less serious but potentially life-threatening condition; Priority 3 "
                "requires non-emergency medical attention; Priority 4 requires essentially "
                "no medical attention. This patient is Priority 2 because chest pain may "
                "represent ACS or another potentially life-threatening condition."
            ),
        },
        {
            "prompt": (
                "The secondary assessment begins. For this responsive medical patient with "
                "chest pain, how will you investigate the pain, and what exactly will you ask?"
            ),
            "concepts": {
                "OPQRST": ["opqrst", "onset", "provocation", "quality", "radiation", "severity", "time"],
                "SAMPLE": ["sample", "symptoms", "allergies", "medications", "past medical", "last oral", "events"],
            },
            "critical": ["OPQRST", "SAMPLE"],
            "first_hint": "Although that step might be important at another time, what should you consider now?",
            "second_hint": "Find the history of this episode. What goes into finding this history?",
            "partial_hint": "You identified {matched}. What other history framework should you use?",
            "completion": (
                "Use OPQRST: onset, provocation/palliation, quality, radiation, severity, and "
                "time. Use SAMPLE: signs/symptoms, allergies, medications, past history, last "
                "oral intake, and events before the call.\n\nThe pain began gradually 20 minutes "
                "ago while doing dishes. It is constant heavy central pressure radiating to the "
                "left arm, 8/10, not relieved by rest and unaffected by breathing, movement, or "
                "palpation. He has nausea and diaphoresis but denies dyspnea, dizziness, syncope, "
                "tearing pain, or back pain. He has no known allergies; takes lisinopril and "
                "atorvastatin; is prescribed sublingual nitroglycerin; and has hypertension, high "
                "cholesterol, and angina. This episode is worse and longer than prior angina. "
                "He ate lunch two hours ago."
            ),
        },
        {
            "prompt": (
                "You have obtained the history of the chest discomfort. "
                "What objective measurements should you obtain next?"
            ),
            "concepts": {
                "heart rate": ["heart rate", "pulse", "hr"],
                "SpO2": ["spo2", "oxygen saturation", "pulse ox"],
                "blood pressure": ["blood pressure", "bp"],
                "blood glucose": ["blood sugar", "blood glucose", "bgl", "glucometer"],
                "temperature": ["temperature", "temp"],
                "respiratory rate": ["respiratory rate", "respirations", "rr"],
                "pupils and skin": ["pupils", "pearrl", "skin"],
            },
            "critical": ["heart rate", "SpO2", "blood pressure", "respiratory rate"],
            "first_hint": (
                "That response does not identify an objective measurement. What measurements "
                "should be included in a complete baseline set?"
            ),
            "context_hints": [
                {
                    "aliases": [
                        "focused exam", "focus exam", "physical exam", "chest exam",
                        "bruise", "bruising", "tenderness", "palpate", "palpation",
                        "originating from chest",
                    ],
                    "feedback": (
                        "A focused examination is important later in the assessment. Right "
                        "now, what objective measurements should you obtain?"
                    ),
                }
            ],
            "second_hint": "We need vital signs. What exact measurements make a thorough baseline set?",
            "partial_hint": "You identified {matched}. What other baseline measurements should you obtain?",
            "completion": (
                "Obtain baseline pulse, SpO₂, blood pressure, blood glucose, temperature, "
                "and respiratory rate; also assess pupils and skin. Findings: pulse 96, regular "
                "and strong; respirations 20, regular and non-labored; BP 146/88; SpO₂ 97% on "
                "room air; temperature 97°F; glucose 100 mg/dL."
            ),
        },
        {
            "prompt": "What else should you examine about the patient?",
            "concepts": {
                "focused chest exam": [
                    "focused exam", "focus exam", "chest exam", "physical exam",
                    "examine chest", "originating from chest", "check chest",
                ],
                "inspect/palpate DCAP-BTLS": [
                    "palpate", "dcap", "deformity", "tenderness", "bruise",
                    "bruising", "contusion", "trauma to chest",
                ],
                "lung sounds": ["lung sounds", "auscultate", "stethoscope"],
                "expose while preserving privacy": ["expose", "clothing", "privacy", "sheet", "gown"],
            },
            "critical": ["focused chest exam", "lung sounds"],
            "first_hint": "Although that step might be important at another time, what should you consider now?",
            "partial_hint": "You identified {matched}. What else belongs in a focused chest examination?",
            "completion": (
                "Conduct a focused chest exam: inspect and palpate for DCAP-BTLS and obtain "
                "lung sounds. Move or remove only enough clothing to assess accurately, explain "
                "the exam, preserve privacy, and cover the patient afterward. This patient has no "
                "abnormal exam findings and no pain with palpation."
            ),
        },
        {
            "prompt": (
                "The findings concern you for suspected acute coronary syndrome. "
                "What treatment will you provide, and what must you verify first?"
            ),
            "concepts": {
                "aspirin": ["aspirin", "asa"],
                "324/325 mg chewed PO": ["324", "325", "chew", "by mouth", "oral", "po"],
                "no aspirin hypersensitivity": ["aspirin allergy", "allergy", "hypersensitivity"],
                "not already fully dosed": ["already taken", "prior aspirin", "full dose", "not given"],
            },
            "critical": ["aspirin", "324/325 mg chewed PO", "no aspirin hypersensitivity", "not already fully dosed"],
            "first_hint": (
                "For suspected ACS, which medication and other BLS "
                "interventions should you consider?"
            ),
            "second_hint": "Aspirin is appropriate, but what must you verify before administering it?",
            "partial_hint": "You identified {matched}. What remaining aspirin requirement must you verify?",
            "completion": (
                "Administer 324 or 325 mg aspirin by mouth and have the patient chew it, "
                "provided there is no known aspirin hypersensitivity and a full dose was not "
                "already received before EMS arrival. The checks are satisfied, so aspirin is given."
            ),
        },
        {
            "prompt": (
                "You are preparing to transport. What should you do after treatment at the "
                "scene and while traveling to the hospital?"
            ),
            "concepts": {
                "ongoing reassessment": [
                    "reassess", "reassessment", "ongoing assessment", "monitor patient",
                ],
                "mental status and ABCs": ["mental status", "avpu", "abc", "airway", "breathing", "circulation"],
                "repeat vital signs/trending": ["repeat vital", "vital signs", "trending", "trend"],
                "chief complaint": ["chief complaint", "pain", "symptoms"],
                "intervention effectiveness": [
                    "intervention", "effectiveness", "response to treatment",
                    "response to medication", "did it help", "helped", "is it working",
                ],
                "5/15-minute frequency": ["5 minute", "five minute", "15 minute", "fifteen minute"],
            },
            "critical": ["ongoing reassessment"],
            "first_hint": "Reassessing the patient is most important now. What should that include?",
            "partial_hint": "You identified {matched}. What else determines whether the condition or response changed?",
            "completion": (
                "Perform ongoing reassessment: mental status and ABCs, repeat vital signs for "
                "trends, reevaluate the chief complaint, and check intervention effectiveness. "
                "Reassess unstable patients at least every 5 minutes and stable patients at least "
                "every 15 minutes, sooner after interventions or condition changes. This stable "
                "patient is reassessed every 15 minutes unless he worsens."
            ),
        },
        {
            "prompt": (
                "The first reassessment shows no significant change, and chest pain remains "
                "unchanged after aspirin. What is your response?"
            ),
            "concepts": {
                "prescribed nitroglycerin": ["nitroglycerin", "nitro", "prescribed"],
                "0.4 mg sublingual": ["0.4", "sublingual", "under tongue", "sl"],
                "SBP above 90": ["90", "systolic", "blood pressure", "bp"],
                "pulse 60-150": ["60", "150", "pulse", "heart rate"],
                "no PAH/PDE medication in 48 hours": ["viagra", "cialis", "levitra", "adcirca", "revatio", "48 hour", "erectile"],
                "maximum three doses": ["maximum 3", "max 3", "three dose", "3 dose"],
                "reassess afterward": ["reassess", "repeat blood pressure", "repeat bp"],
            },
            "critical": ["prescribed nitroglycerin", "0.4 mg sublingual", "SBP above 90", "pulse 60-150", "no PAH/PDE medication in 48 hours"],
            "first_hint": (
                "Chest pain continues after aspirin. What other BLS medication may be "
                "appropriate for this patient?"
            ),
            "second_hint": "Assisting with nitroglycerin may be appropriate. What must you verify first?",
            "partial_hint": "You identified {matched}. What other nitroglycerin safety requirement remains?",
            "completion": (
                "Assist with one dose of the patient's prescribed nitroglycerin, 0.4 mg SL. "
                "Verify it is prescribed, SBP is not below 90, pulse is 60-150, the patient is "
                "at least 13, no listed PAH or erectile-dysfunction medication was taken within "
                "48 hours, and fewer than three total doses were received. It may repeat every "
                "3-5 minutes while criteria remain met, to three total doses. Here, BP is 146/88, "
                "pulse 96, contraindicated medications are denied, so 0.4 mg SL is assisted and "
                "the patient is reassessed."
            ),
        },
        {
            "prompt": (
                "You begin transport. Because this is a Priority 2 patient, what communication "
                "should you make to the receiving hospital, and what information should you provide?"
            ),
            "concepts": {
                "EMRC hospital notification": ["emrc", "hospital notification", "notify hospital"],
                "age and gender": ["age", "62", "gender", "male"],
                "chief complaint": ["chief complaint", "chest pain", "acs"],
                "clinical priority": ["priority 2", "priority two", "clinical priority"],
                "ETA": ["eta", "estimated time"],
                "vitals/treatments/response": ["vital", "treatment", "aspirin", "nitro", "response"],
            },
            "critical": ["EMRC hospital notification"],
            "first_hint": (
                "A Priority 2 patient requires hospital notification. How will you contact "
                "the receiving hospital and what essential information will you provide?"
            ),
            "partial_hint": "You identified {matched}. What required notification information is still missing?",
            "completion": (
                "Contact EMRC and request a Priority 2 notification to Suburban Hospital. "
                "For example: “EMRC, Ambulance A2 requesting a Priority 2 notification to "
                "Suburban.” Report at minimum the patient's age and gender, chief complaint, "
                "clinical priority, and ETA. Add pertinent vitals, treatments, and response "
                "when appropriate. Hospital notification is distinct from medical consultation."
            ),
        },
        {
            "prompt": (
                "You arrive at Suburban Hospital without a significant change. "
                "What should you do after bringing the patient into the emergency department?"
            ),
            "concepts": {
                "verbal handoff/transfer": [
                    "handoff", "transfer care", "transfer of care", "report",
                    "receiving nurse", "clinician",
                ],
                "demographics/complaint/priority": ["age", "gender", "chief complaint", "priority"],
                "history/assessment": ["history", "assessment", "opqrst", "sample"],
                "initial and trending vitals": ["vital", "trend", "initial"],
                "treatments/doses/response": ["treatment", "dose", "aspirin", "nitro", "response"],
                "transport changes/events": ["change", "event", "transport"],
            },
            "critical": ["verbal handoff/transfer"],
            "first_hint": (
                "You must formally transfer responsibility to a hospital clinician. "
                "Who should you speak with?"
            ),
            "second_hint": (
                "Provide a verbal handoff to the receiving nurse or clinician. "
                "What important information belongs in it?"
            ),
            "partial_hint": "You identified {matched}. What other assessment, treatment, response, or trend information is needed?",
            "completion": (
                "Give an organized verbal handoff to the receiving nurse or clinician assuming "
                "responsibility. Include age/gender, chief complaint and priority, relevant history "
                "and assessment, initial and trending vital signs, treatments and doses, response, "
                "reassessments, and significant transport events. Relay the assessment findings and "
                "treatment to the person assuming responsibility."
            ),
        },
        {
            "prompt": (
                "After verbal handoff and transfer to the hospital clinician, "
                "what remains to be completed?"
            ),
            "concepts": {
                "PCR/ePCR in eMEDS": ["pcr", "epcr", "patient care report", "emeds"],
                "accurate narrative": ["narrative", "chart", "document", "documentation"],
                "submit to receiving facility": ["submit", "receiving facility", "hospital copy"],
            },
            "critical": ["PCR/ePCR in eMEDS"],
            "first_hint": "The patient is transferred, but the call still needs documentation. What report should you complete?",
            "partial_hint": "You identified {matched}. What else completes the documentation process?",
            "completion": (
                "Complete the Patient Care Report in eMEDS according to jurisdictional "
                "procedures and submit the required documentation to the receiving facility. "
                "The narrative should accurately describe the call, assessment, care, "
                "reassessments, and transfer. A department-taught format such as CHART may "
                "organize the narrative."
            ),
        },
    ],
}
