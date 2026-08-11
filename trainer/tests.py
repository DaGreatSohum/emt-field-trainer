import json

from django.test import TestCase
from django.core.cache import cache
from django.test import Client

from .models import TrainingAttempt
from .views import SCENARIOS


REALISTIC_HAPPY_PATHS = {
    "chest_pain": [
        "oxygen, cot, AED and my jumpbag",
        "Gloves on. Is my scene sftey, is this my only pt, and should I call ALS?",
        "I want to look for immediate lifethreats and decide whether he is critically unstable.",
        "I introduce myself and check his mental status using AVPU.",
        "He is alert, the A in AVPU, because he answered spontaneously.",
        "Assess ABCs: confirm a clear airway, watch breathing, then check pulse and circulation.",
        "Assign a clinical priority; this chest pain patient is Priority 2.",
        "I ask a full OPQRST and SAMPLE history.",
        "Baseline vitals: HR, RR, BP and SpO2.",
        "Do a focused chest exam and listen to lung sounds.",
        "Give 324 mg chewable aspirin after verifying no aspirin allergy and no full dose already taken.",
        "Ongoing reassessment: mental status and ABCs, trend repeat vitals, ask about his pain, and see if aspirin helped.",
        "Assist his prescribed nitro 0.4 mg SL after confirming SBP over 90, pulse 60-150, no Viagra/Cialis/Revatio in 48 hours, then reassess.",
        "Call EMRC for a Priority 2 hospital notification: 62yo male, chest pain/ACS, ETA 10 minutes, plus vitals and treatments.",
        "Give the receiving nurse a handoff with age, complaint and priority, history and assessment, initial/trending vitals, med doses/response, and transport changes.",
        "Complete and submit the PCR/ePCR in eMEDS with an accurate narrative.",
    ],
    "breathing": [
        "airway bag, oxygen, BVM, suction, neb supplies, cot",
        "gloves, check scene saftey, determine if this is the only patient and call ALS",
        "Sit upright, assess ABCs and SpO2, give oxygen if needed and albuterol; call ALS and keep the BVM ready.",
        "Assist ventilations with BVM and oxygen, get an ALS intercept, transport priority, and reassess continuously.",
    ],
    "anaphylaxis": [
        "jump bag, oxygen, airway bag, epi, albuterol, monitor and cot",
        "PPE, ensure a safe scene, count patients, request paramedics",
        "Assess airway and ABCs, give IM epinephrine and oxygen, remove the stinger and call ALS.",
        "Continue airway/oxygen and shock care, transport rapidly, reassess and have ALS consider more epi per protocol.",
    ],
    "hypoglycemia": [
        "green bag, glucometer, oral glucose, airway gear and cot",
        "gloves, scene safe, one patient, consider if extra resources are needed",
        "Start with ABCs, assess mental status and check a finger-stick blood glucose.",
        "If he can swallow, give oral glucose between gum and cheek, protect airway, and recheck glucose.",
    ],
    "seizure": [
        "primary bag, oxygen, suction, BVM, glucometer, monitor and cot",
        "wear PPE, scene is safe, only one pt, call ALS",
        "Do not restrain; protect from injury, time the seizure, manage airway with oxygen/suction, and check glucose.",
        "Recovery position, reassess ABCs and vitals, get witness/SAMPLE history, check injuries and transport.",
    ],
    "stroke": [
        "jumpbag, glucometer, oxygen/airway gear, monitor, cot and stair chair",
        "gloves, check hazards/scene safety, ask if more patients, request ALS",
        "ABCs, Cincinnati stroke scale/LAMS, blood sugar, last known well and ask about blood thinners.",
        "Rapid transport to an appropriate stroke center, call a prearrival stroke alert, monitor and reassess.",
    ],
    "overdose": [
        "PPE, airway bag, BVM, oxygen, suction, Narcan, AED and cot",
        "gloves and needle safety, safe scene, one patient, ALS requested",
        "Make sure scene is safe, use PPE, check pulse and airway, suction and ventilate with BVM; have AED and ALS.",
        "Ventilate with BVM and oxygen first, give naloxone, aiming for adequate breathing not necessarily awake, transport and monitor.",
    ],
    "burns": [
        "PPE, airway/oxygen, clean dry sheets, mylar blanket, trauma bag and cot",
        "PPE, make sure scene is sfate, only one pt, request fire/ALS resources",
        "Stop the burning, remove wet clothes/jewelry, assess airway for soot/inhalation, no ice, keep warm, estimate depth and TBSA, cover dry.",
        "Rapid priority transport to a burn center, oxygen and airway readiness, prevent hypothermia, pain care and reassessment.",
    ],
    "major_trauma": [
        "PPE, trauma bag, tourniquets, airway/oxygen/suction, chest seals, pelvic binder and cot",
        "gloves, scene safety, determine patient count, request rescue and ALS",
        "Control massive hemorrhage, assess ABCs with c-spine precautions, and identify mechanism/resources.",
        "Treat shock and keep warm, apply pelvic binder, call ALS, rapid transport to trauma center and reassess.",
    ],
    "cardiac_arrest": [
        "PPE, AED, BVM, oxygen, suction, airway bag and cot",
        "gloves, safe scene, confirm one patient, request ALS/additional unit",
        "Check responsiveness, breathing and pulse under 10 seconds, start high quality CPR 100-120, apply AED, BVM and assign roles.",
        "Clear and shock, immediately resume CPR for 2 minutes, keep pauses under 10 seconds, ALS and reanalyze rhythm.",
    ],
}

REALISTIC_HAPPY_PATHS.update({
    "chf": ["oxygen, airway bag, CPAP, monitor, cot", "gloves, scene safe, one patient, request ALS", "Sit high Fowler, assess ABCs/work of breathing and SpO2, give oxygen and call ALS.", "Assist ventilation with BVM, rapid transport Priority 1, ALS, and reassess."],
    "pediatric_asthma": ["pediatric airway bag, oxygen, BVM, nebulizer, cot", "PPE, safe scene, one child, call ALS", "Use the pediatric assessment triangle, check ABCs and pulse ox, give albuterol and oxygen, call ALS.", "Use a pediatric BVM, rapid transport, ALS, and continuous reassessment."],
    "syncope": ["primary bag, glucose meter, oxygen, monitor, cot", "gloves, scene safety, one patient, consider ALS", "Assess ABCs, lay supine, check glucose, stroke signs and injuries from the fall.", "Get SAMPLE history and vitals, cardiac monitor, transport, and reassess."],
    "sepsis": ["PPE, thermometer, glucose meter, oxygen, monitor, cot", "PPE, safe scene, patient count, ALS", "Assess ABCs, look for infection and sepsis criteria including temperature, HR, RR and BP, and check glucose.", "Shock care, Priority 1 rapid transport, sepsis alert, and ALS."],
    "heat_emergency": [
        "thermometer, cooling packs, wet sheets, oxygen and cot",
        "gloves, safe scene, one patient, request ALS",
        "Form a general impression and look for immediate life threats and critical instability.",
        "Introduce myself and assess mental status with AVPU.",
        "Continue the initial assessment and check ABCs.",
        "Assign a clinical priority: he is Priority 1.",
        "Check temperature and heat exposure history, move him to a cool environment, and remove excess clothing; suspect heat stroke.",
        "Aggressive cooling with wet sheets, mist/fan and ice packs, rapid transport, ALS, and repeated reassessment.",
    ],
    "carbon_monoxide": ["PPE, fire/hazmat monitor, high-flow oxygen, co-oximeter and cot", "PPE, ensure scene safety, count all patients, request fire/hazmat", "Do not enter; remove from exposure, request resources for multiple patients, assess ABCs and give high-flow oxygen.", "Pulse ox can be unreliable in CO; continue 100 percent oxygen, transport to appropriate hospital, and reassess."],
    "submersion": ["water rescue PPE, oxygen, suction, BVM, warming blankets, AED and cot", "PPE, safe scene, one patient, request ALS", "Rescuer safety first, then ABCs, prevent hypothermia and ask submersion time.", "Give oxygen or BVM support, request ALS, rapid transport and reassess SpO2."],
    "spinal_injury": ["trauma bag, collars, scoop, oxygen and cot", "gloves, scene safety, one patient, call ALS", "Manual inline stabilization, assess ABCs and neurologic SMR criteria, apply a cervical collar.", "Minimize movement with SMR equipment, check PMS before and after, transport and reassess."],
    "agitation": ["PPE, primary bag, glucose meter, airway bag, monitor and cot", "PPE, safe scene, one patient, request police/ALS if needed", "Ensure scene safety with law enforcement, verbally de-escalate, and assess capacity, substances and medical causes.", "Keep him non-prone, monitor vitals/glucose/temperature, transport and call ALS."],
    "childbirth": ["OB kit, PPE, neonatal BVM, suction, warming blankets and cot", "gloves, scene safe, one mother, request ALS", "Assess ABCs, crowning/contractions, bleeding and OB history, prepare OB kit.", "Support the head and baby, check nuchal cord, dry warm and assess newborn ABCs, manage mother/placenta and transport."],
})

for _scenario_key, _clinical_position in {
    "hypoglycemia": 1,
    "seizure": 1,
    "stroke": 1,
    "syncope": 1,
    "sepsis": 1,
    "heat_emergency": 3,
    "carbon_monoxide": 1,
    "spinal_injury": 1,
    "agitation": 1,
}.items():
    REALISTIC_HAPPY_PATHS[_scenario_key].insert(
        2 + _clinical_position,
        "Assess A&O x4: person, place, time, and situation/event.",
    )

for _scenario_key in set(REALISTIC_HAPPY_PATHS) - {"chest_pain"}:
    REALISTIC_HAPPY_PATHS[_scenario_key].extend([
        "Continue indicated care, reassess ABCs, monitor response, and repeat/trend vital signs.",
        "Notify the hospital with patient age, chief complaint, clinical priority, ETA, vital signs, treatments and response.",
        "Give a verbal handoff with assessment, treatments and trends, and transfer care to the receiving nurse.",
        "Complete and submit the PCR/ePCR in eMEDS with an accurate narrative.",
    ])


class TrainerApiTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_browser_homepage_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Choose your next call")
        self.assertContains(response, "Call 1: Chest Pain")

    def test_lists_twenty_scenarios(self):
        response = self.client.get("/api/scenarios/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["scenarios"]), 20)

    def test_every_scenario_has_ungraded_tailored_equipment_coaching(self):
        equipment_responses = set()
        for scenario_key, scenario in SCENARIOS.items():
            first_step = scenario["steps"][0]
            self.assertFalse(first_step["graded"], scenario_key)
            self.assertTrue(first_step["advance_always"], scenario_key)
            self.assertIn(
                "Equipment selections are not graded in this training app",
                first_step["completion"],
            )
            equipment_responses.add(first_step["completion"])

            attempt_id = self.client.post(
                f"/api/scenarios/{scenario_key}/start/"
            ).json()["attempt_id"]
            result = self._respond(attempt_id, "I do not know.").json()
            self.assertTrue(result["advanced"], scenario_key)
            self.assertIsNone(result["step_score"], scenario_key)
            self.assertEqual(result["overall_score"], 0, scenario_key)
            self.assertEqual(result["feedback"], first_step["completion"], scenario_key)

        self.assertEqual(len(equipment_responses), len(SCENARIOS))

    def test_every_scenario_recognizes_natural_scene_sizeup_language(self):
        response = (
            "I will wear gloves. Is the scene safe? Is this my only pt? "
            "I will call ALS and additional units."
        )
        for scenario_key in SCENARIOS:
            attempt_id = self.client.post(
                f"/api/scenarios/{scenario_key}/start/"
            ).json()["attempt_id"]
            self._respond(attempt_id, "Whatever equipment is appropriate.")
            result = self._respond(attempt_id, response).json()
            self.assertTrue(result["advanced"], scenario_key)
            self.assertEqual(result["step"], 3, scenario_key)
            self.assertEqual(result["missed"], [], scenario_key)

    def test_forced_clinical_advance_never_falsely_says_complete(self):
        attempt_id = self.client.post("/api/scenarios/breathing/start/").json()["attempt_id"]
        self._respond(attempt_id, "equipment")
        self._respond(
            attempt_id,
            "Gloves, scene safety, one patient, and request ALS.",
        )
        for _ in range(3):
            result = self._respond(attempt_id, "I do not know.").json()
        self.assertTrue(result["advanced"])
        self.assertNotIn("Complete response", result["feedback"])
        self.assertIn("Position the patient", result["feedback"])

    def test_realistic_happy_paths_complete_every_scenario_first_try(self):
        self.assertEqual(set(REALISTIC_HAPPY_PATHS), set(SCENARIOS))
        for scenario_key, answers in REALISTIC_HAPPY_PATHS.items():
            self.assertEqual(len(answers), len(SCENARIOS[scenario_key]["steps"]))
            attempt_id = self.client.post(
                f"/api/scenarios/{scenario_key}/start/"
            ).json()["attempt_id"]
            for expected_step, answer in enumerate(answers, start=1):
                result = self._respond(attempt_id, answer).json()
                self.assertTrue(
                    result["advanced"],
                    f"{scenario_key} step {expected_step} failed: "
                    f"matched={result['matched']} missed={result['critical_missed']}",
                )
                if expected_step < len(answers):
                    self.assertFalse(
                        result["completed"],
                        f"{scenario_key} completed early at step {expected_step}",
                    )
            self.assertTrue(result["completed"], scenario_key)
            self.assertEqual(result["overall_score"], 100, scenario_key)

    def test_priority_shorthand_p2_means_priority_2(self):
        scenario = SCENARIOS["chest_pain"]
        priority_step = scenario["steps"][6]
        from .views import _match_concepts
        matched = _match_concepts("P2", priority_step["concepts"])
        self.assertIn("Priority 2", matched)
        self.assertIn("assign clinical priority", matched)

    def test_bruising_is_acknowledged_as_focused_exam_direction(self):
        focused_step = SCENARIOS["chest_pain"]["steps"][9]
        from .views import _match_concepts
        matched = _match_concepts(
            "I need to make sure it is not a bruise and maybe not originating from the chest",
            focused_step["concepts"],
        )
        self.assertIn("focused chest exam", matched)
        self.assertIn("inspect/palpate DCAP-BTLS", matched)
        self.assertIn("lung sounds", focused_step["critical"])

    def test_bruising_during_vitals_is_identified_as_important_later(self):
        vitals_step = SCENARIOS["chest_pain"]["steps"][8]
        from .views import _context_hint
        self.assertIn(
            "important later",
            _context_hint("maybe it is a bruise", vitals_step),
        )
        self.assertIsNone(_context_hint("vita", vitals_step))
        self.assertNotIn("exam", vitals_step["first_hint"].lower())
        self.assertNotIn("bruis", vitals_step["first_hint"].lower())

    def test_orientation_checkpoint_is_scoped_to_responsive_neurologic_calls(self):
        included = {
            "hypoglycemia", "seizure", "stroke", "syncope", "sepsis",
            "heat_emergency", "carbon_monoxide", "spinal_injury", "agitation",
        }
        for scenario_key, scenario in SCENARIOS.items():
            has_orientation = any(
                "focused neurologic and mental-status" in step["prompt"]
                for step in scenario["steps"]
            )
            self.assertEqual(has_orientation, scenario_key in included, scenario_key)

    def test_heat_orientation_before_abcs_gets_contextual_redirect(self):
        from .views import _context_hint
        abc_step = next(
            step for step in SCENARIOS["heat_emergency"]["steps"]
            if "what part of the initial assessment comes next" in step["prompt"].lower()
        )
        feedback = _context_hint(
            "Evaluate AOx4: person, place, time, and event.",
            abc_step,
        )
        self.assertIn("useful for the focused neurologic assessment", feedback)
        self.assertIn("immediate threats", feedback)

    def test_orientation_answers_accumulate_across_natural_phrasing(self):
        from .standard_steps import ORIENTATION_STEP
        from .views import _match_concepts
        first = _match_concepts("oriented", ORIENTATION_STEP["concepts"])
        second = _match_concepts(
            "name, place, time, events",
            ORIENTATION_STEP["concepts"],
        )
        self.assertIn("orientation/A&O x4", first)
        self.assertIn("person, place, time, and situation/event", second)
        self.assertEqual(
            set(first + second),
            set(ORIENTATION_STEP["critical"]),
        )

    def test_heat_priority_2_gets_specific_correction(self):
        from .views import _context_hint
        priority_step = next(
            step for step in SCENARIOS["heat_emergency"]["steps"]
            if "final initial-assessment decision" in step["prompt"]
        )
        for wording in ("P2", "Priority 2", "priority two"):
            feedback = _context_hint(wording, priority_step)
            self.assertIn("Priority 2 is not appropriate", feedback)
            self.assertIn("altered mental status", feedback)

    def test_every_declared_alias_matches_its_own_concept(self):
        from .views import _match_concepts
        for scenario_key, scenario in SCENARIOS.items():
            for step_number, step in enumerate(scenario["steps"], start=1):
                for concept, aliases in step["concepts"].items():
                    self.assertTrue(
                        aliases,
                        f"{scenario_key} step {step_number}: {concept} has no aliases",
                    )
                    for alias in aliases:
                        self.assertIn(
                            concept,
                            _match_concepts(alias, step["concepts"]),
                            f"{scenario_key} step {step_number}: {alias!r}",
                        )

    def test_gibberish_never_earns_a_concept_in_any_scenario(self):
        from .views import _match_concepts
        noise = (
            "dddd", "asdf", "not sure", "I don't know", "maybe",
            "help", "do something", "whatever",
        )
        for scenario_key, scenario in SCENARIOS.items():
            for step_number, step in enumerate(scenario["steps"], start=1):
                for answer in noise:
                    self.assertEqual(
                        _match_concepts(answer, step["concepts"]),
                        [],
                        f"{scenario_key} step {step_number}: {answer!r}",
                    )

    def test_all_graded_steps_have_requirements_hints_and_teaching(self):
        for scenario_key, scenario in SCENARIOS.items():
            for step_number, step in enumerate(scenario["steps"], start=1):
                if not step.get("graded", True):
                    continue
                self.assertTrue(
                    step.get("critical") or step.get("minimum_matches"),
                    f"{scenario_key} step {step_number} has no progression requirement",
                )
                self.assertTrue(
                    step.get("first_hint"),
                    f"{scenario_key} step {step_number} has no first hint",
                )
                self.assertTrue(
                    step.get("completion"),
                    f"{scenario_key} step {step_number} has no teaching response",
                )

    def test_split_orientation_answers_advance_through_api(self):
        attempt_id = self.client.post(
            "/api/scenarios/hypoglycemia/start/"
        ).json()["attempt_id"]
        self._respond(attempt_id, "equipment")
        self._respond(
            attempt_id,
            "PPE, scene safety, one patient, no extra resources needed",
        )
        self._respond(attempt_id, "Assess ABCs and check blood glucose")

        first = self._respond(attempt_id, "oriented").json()
        self.assertFalse(first["advanced"])
        self.assertIn("orientation/A&O x4", first["matched"])

        second = self._respond(
            attempt_id,
            "name, place, time, events",
        ).json()
        self.assertTrue(second["advanced"])
        self.assertEqual(second["missed"], [])

    def test_priority_shorthand_is_consistent_across_relevant_calls(self):
        from .views import _match_concepts
        chest_priority = SCENARIOS["chest_pain"]["steps"][6]
        heat_priority = next(
            step for step in SCENARIOS["heat_emergency"]["steps"]
            if "final initial-assessment decision" in step["prompt"]
        )
        sepsis_priority = next(
            step for step in SCENARIOS["sepsis"]["steps"]
            if "BP is 82/48" in step["prompt"]
        )
        self.assertIn("Priority 2", _match_concepts("P2", chest_priority["concepts"]))
        self.assertIn("Priority 1", _match_concepts("P1", heat_priority["concepts"]))
        self.assertIn(
            "priority 1 transport",
            _match_concepts("P1 rapid transport", sepsis_priority["concepts"]),
        )

    def test_orientation_domains_accept_any_order_and_natural_questions(self):
        from itertools import permutations
        from .standard_steps import ORIENTATION_STEP
        from .views import _match_concepts

        expected = set(ORIENTATION_STEP["critical"])
        for ordering in permutations(("name", "date/time", "events", "place")):
            answer = ", ".join(ordering)
            self.assertEqual(
                set(_match_concepts(answer, ORIENTATION_STEP["concepts"])),
                expected,
                answer,
            )

        natural_answers = (
            "I ask his name, where he is, what year it is, and what happened.",
            "Who is the president, what time is it, where are we, and what led up to this incident?",
            "Ask where she is located, the events leading here, her name, and today's date.",
            "Person, situation, place, and time.",
        )
        for answer in natural_answers:
            self.assertEqual(
                set(_match_concepts(answer, ORIENTATION_STEP["concepts"])),
                expected,
                answer,
            )

    def test_every_scenario_requires_transfer_and_documentation_before_completion(self):
        for scenario_key, scenario in SCENARIOS.items():
            final_prompts = [step["prompt"].lower() for step in scenario["steps"][-2:]]
            self.assertTrue(
                "receiving" in final_prompts[0]
                or "hospital" in final_prompts[0]
                or "emergency department" in final_prompts[0],
                scenario_key,
            )
            self.assertTrue(
                "transfer" in final_prompts[1] or "handoff" in final_prompts[1],
                scenario_key,
            )

    def test_heat_treatment_retry_advances_to_transport_not_completion(self):
        answers = REALISTIC_HAPPY_PATHS["heat_emergency"]
        attempt_id = self.client.post(
            "/api/scenarios/heat_emergency/start/"
        ).json()["attempt_id"]
        # Reach the final heat-treatment phase, immediately before the four closure steps.
        for answer in answers[:-5]:
            result = self._respond(attempt_id, answer).json()
            self.assertTrue(result["advanced"])

        first = self._respond(
            attempt_id,
            "I will reassess and start aggressive cooling.",
        ).json()
        self.assertFalse(first["completed"])
        self.assertFalse(first["advanced"])

        self._respond(attempt_id, "I would do a focused exam.")
        third = self._respond(attempt_id, "I am not sure.").json()
        self.assertTrue(third["advanced"])
        self.assertFalse(third["completed"])
        self.assertIn("transport has begun", third["prompt"].lower())

    def test_split_end_of_call_answers_complete_all_non_chest_scenarios(self):
        for scenario_key in set(SCENARIOS) - {"chest_pain"}:
            answers = REALISTIC_HAPPY_PATHS[scenario_key]
            attempt_id = self.client.post(
                f"/api/scenarios/{scenario_key}/start/"
            ).json()["attempt_id"]

            # Complete preparation and clinical care, stopping before common closure.
            for answer in answers[:-4]:
                result = self._respond(attempt_id, answer).json()
                self.assertTrue(result["advanced"], scenario_key)
                self.assertFalse(result["completed"], scenario_key)

            transport = self._respond(
                attempt_id,
                "Reassess ABCs and repeat vitals.",
            ).json()
            self.assertTrue(transport["advanced"], scenario_key)
            self.assertFalse(transport["completed"], scenario_key)

            notification = self._respond(
                attempt_id,
                "Give a prearrival hospital notification.",
            ).json()
            self.assertTrue(notification["advanced"], scenario_key)
            self.assertFalse(notification["completed"], scenario_key)

            transfer = self._respond(
                attempt_id,
                "Give a verbal handoff and transfer care to the receiving nurse.",
            ).json()
            self.assertTrue(transfer["advanced"], scenario_key)
            self.assertFalse(transfer["completed"], scenario_key)

            complete = self._respond(
                attempt_id,
                "Complete and submit the PCR in eMEDS with an accurate narrative.",
            ).json()
            self.assertTrue(complete["advanced"], scenario_key)
            self.assertTrue(complete["completed"], scenario_key)

    def test_every_dispatch_provides_age_and_sex_or_an_estimate(self):
        for scenario_key, scenario in SCENARIOS.items():
            dispatch = scenario["dispatch"].lower()
            self.assertIn("patient information:", dispatch, scenario_key)
            self.assertRegex(dispatch, r"(year-old|approximately)", scenario_key)
            self.assertRegex(dispatch, r"(male|female)", scenario_key)

    def test_web_completion_stays_on_transcript_with_corner_notice(self):
        from pathlib import Path
        base = Path(__file__).resolve().parent.parent
        script = (base / "web" / "web-app.js").read_text()
        markup = (base / "web" / "index.html").read_text()
        self.assertIn('id="completion-toast"', markup)
        self.assertNotIn('setTimeout(() => show("result-view")', script)
        self.assertIn('$("#completion-toast").classList.remove("hidden")', script)
        self.assertIn('$("#response-input").disabled = true', script)

    def test_exact_reported_heat_sequence_is_understood(self):
        attempt_id = self.client.post(
            "/api/scenarios/heat_emergency/start/"
        ).json()["attempt_id"]
        for answer in REALISTIC_HAPPY_PATHS["heat_emergency"][:7]:
            result = self._respond(attempt_id, answer).json()
            self.assertTrue(result["advanced"])

        first_assessment = self._respond(
            attempt_id,
            "history, aggressive cooling",
        ).json()
        self.assertFalse(first_assessment["advanced"])
        self.assertIn("heat exposure/history", first_assessment["matched"])
        self.assertIn("Active cooling is appropriate treatment", first_assessment["feedback"])

        second_assessment = self._respond(
            attempt_id,
            "moving to cooler place, take off excessive clothing, "
            "figure out history of episode, cooling packs",
        ).json()
        self.assertFalse(second_assessment["advanced"])
        self.assertIn("remove from heat", second_assessment["matched"])
        self.assertIn("remove excess clothing", second_assessment["matched"])

        assessment_review = self._respond(attempt_id, "not sure").json()
        self.assertTrue(assessment_review["advanced"])
        self.assertFalse(assessment_review["completed"])

        cooling = self._respond(
            attempt_id,
            "aggressive cooling systems, cool ambulance, reassess",
        ).json()
        self.assertFalse(cooling["advanced"])
        als = self._respond(attempt_id, "calling ALS").json()
        self.assertFalse(als["advanced"])
        transport = self._respond(attempt_id, "hospital").json()
        self.assertTrue(transport["advanced"])
        self.assertFalse(transport["completed"])

        ongoing = self._respond(
            attempt_id,
            "reassess every 5 min, cooling care, transport to hospital, "
            "hospital notification",
        ).json()
        self.assertTrue(ongoing["advanced"])

        notification = self._respond(
            attempt_id,
            "ETA, heat stroke as CC, 25 y/o male",
        ).json()
        self.assertTrue(notification["advanced"])
        self.assertIn("hospital notification", notification["matched"])
        self.assertIn("patient/complaint/priority", notification["matched"])

    def test_typo_tolerance_does_not_require_exact_keywords(self):
        attempt_id = self.client.post("/api/scenarios/chest_pain/start/").json()["attempt_id"]
        self._respond(attempt_id, "whatever equipment")
        scene = self._respond(
            attempt_id,
            "glvoes, check scene sftey, is this my only pt, request additonal ALS units",
        ).json()
        self.assertTrue(scene["advanced"])
        impression = self._respond(
            attempt_id,
            "I am looking for any apparent lifethreats.",
        ).json()
        self.assertTrue(impression["advanced"])
        self.assertIn("general impression", impression["matched"])

    def test_scene_sizeup_accepts_multiple_real_world_phrasings(self):
        variations = [
            "PPE on. Any hazards? How many patients are there? No extra resources needed.",
            "Take BSI precautions, confirm a safe scene, get a patient count, and upgrade with a medic unit.",
            "Gloves. Is it safe? Are there any other pts? Should we request an engine?",
            "glvoes on, check scene sftey, only one patinet, call additonal ALS units",
        ]
        for wording in variations:
            attempt_id = self.client.post("/api/scenarios/stroke/start/").json()["attempt_id"]
            self._respond(attempt_id, "equipment")
            result = self._respond(attempt_id, wording).json()
            self.assertTrue(
                result["advanced"],
                f"{wording}: matched={result['matched']} missed={result['critical_missed']}",
            )

    def test_naming_scene_sizeup_gets_acknowledged_not_rejected(self):
        for scenario_key in SCENARIOS:
            attempt_id = self.client.post(
                f"/api/scenarios/{scenario_key}/start/"
            ).json()["attempt_id"]
            self._respond(attempt_id, "equipment")
            result = self._respond(attempt_id, "scene size up").json()
            self.assertFalse(result["advanced"], scenario_key)
            self.assertEqual(
                result["matched"],
                ["Scene Arrival and Size-Up"],
                scenario_key,
            )
            self.assertIn("You identified Scene Arrival and Size-Up", result["feedback"])
            self.assertNotIn("another time", result["feedback"])

    def test_general_impression_accepts_valid_umbrella_responses(self):
        variations = [
            "I assess for immediate life threats.",
            "I form a general impression and decide if he is critically unstable.",
            "Check AVPU for altered mental status.",
            "Look for airway compromise.",
            "Assess for respiratory distress and signs of poor perfusion.",
        ]
        for wording in variations:
            attempt_id = self.client.post("/api/scenarios/chest_pain/start/").json()["attempt_id"]
            self._respond(attempt_id, "equipment")
            self._respond(
                attempt_id,
                "gloves, scene safety, one patient, request ALS",
            )
            result = self._respond(attempt_id, wording).json()
            self.assertTrue(
                result["advanced"],
                f"{wording}: matched={result['matched']}",
            )

    def test_off_topic_answers_do_not_pass_graded_clinical_steps(self):
        for scenario_key in SCENARIOS:
            attempt_id = self.client.post(
                f"/api/scenarios/{scenario_key}/start/"
            ).json()["attempt_id"]
            self._respond(attempt_id, "equipment")
            self._respond(
                attempt_id,
                "gloves, scene safety, one patient, request ALS",
            )
            result = self._respond(
                attempt_id,
                "I would complete paperwork and clean the ambulance.",
            ).json()
            self.assertFalse(result["advanced"], scenario_key)
            self.assertEqual(result["matched"], [], scenario_key)

    def test_pulse_ox_does_not_count_as_pulse_or_heart_rate(self):
        attempt_id = self.client.post("/api/scenarios/chest_pain/start/").json()["attempt_id"]
        self._respond(attempt_id, "equipment")
        self._respond(attempt_id, "gloves, scene safety, one patient, ALS")
        self._respond(attempt_id, "life threats")
        self._respond(attempt_id, "mental status")
        self._respond(attempt_id, "alert")
        result = self._respond(
            attempt_id,
            "The airway is patent, breathing is adequate, and I apply a pulse ox.",
        ).json()
        self.assertFalse(result["advanced"])
        self.assertNotIn("circulation/pulse", result["matched"])

    def test_struggling_learner_flow_completes_safely_in_every_scenario(self):
        for scenario_key, scenario in SCENARIOS.items():
            attempt_id = self.client.post(
                f"/api/scenarios/{scenario_key}/start/"
            ).json()["attempt_id"]
            equipment = self._respond(attempt_id, "I am not sure.").json()
            self.assertTrue(equipment["advanced"], scenario_key)
            self.assertNotIn("Complete response", equipment["feedback"])

            for step_number in range(2, len(scenario["steps"]) + 1):
                for attempt_number in range(1, 4):
                    result = self._respond(attempt_id, "I am not sure.").json()
                    if attempt_number < 3:
                        self.assertFalse(
                            result["advanced"],
                            f"{scenario_key} step {step_number} advanced before teaching",
                        )
                    else:
                        self.assertTrue(
                            result["advanced"],
                            f"{scenario_key} step {step_number} did not resolve",
                        )
                        self.assertNotIn("Complete response", result["feedback"])
            self.assertTrue(result["completed"], scenario_key)
            self.assertEqual(result["overall_score"], 0, scenario_key)

    def _respond(self, attempt_id, response):
        return self.client.post(
            f"/api/attempts/{attempt_id}/respond/",
            data=json.dumps({"response": response}),
            content_type="application/json",
        )

    def test_chest_pain_uses_progressive_same_step_coaching(self):
        started = self.client.post("/api/scenarios/chest_pain/start/").json()
        attempt_id = started["attempt_id"]
        equipment = self._respond(
            attempt_id,
            "Gloves, jump bag, oxygen, BVM, suction, AED, and aspirin.",
        ).json()
        self.assertTrue(equipment["advanced"])
        self.assertEqual(equipment["step"], 2)

        body = self._respond(attempt_id, "I take a blood pressure.").json()
        self.assertFalse(body["completed"])
        self.assertFalse(body["advanced"])
        self.assertEqual(body["step"], 2)
        self.assertIn("what should you consider now", body["feedback"])

        body = self._respond(attempt_id, "I obtain a SAMPLE history.").json()
        self.assertFalse(body["advanced"])
        self.assertEqual(body["step"], 2)
        self.assertIn("Scene Size-Up", body["feedback"])

        body = self._respond(
            attempt_id,
            "BSI with gloves, confirm scene safety, one patient, and request ALS.",
        ).json()
        self.assertTrue(body["advanced"])
        self.assertEqual(body["step"], 3)
        self.assertIn("complete scene size-up", body["feedback"])
        self.assertIn("ALS", body["feedback"])

    def test_scene_sizeup_recognizes_natural_patient_count_question(self):
        attempt_id = self.client.post("/api/scenarios/chest_pain/start/").json()["attempt_id"]
        self._respond(attempt_id, "Primary bag, oxygen, cot, and stair chair.")

        first = self._respond(
            attempt_id,
            "Is the scene safe, do I have proper gloves on, is this my only pt?",
        ).json()
        self.assertFalse(first["advanced"])
        self.assertCountEqual(
            first["matched"],
            ["BSI/PPE", "scene safety", "number of patients"],
        )
        self.assertEqual(first["missed"], ["additional resources"])

        second = self._respond(
            attempt_id,
            "I will call additional units (ALS paramedics), determine this is an NOI, "
            "and consider c-spine.",
        ).json()
        self.assertTrue(second["advanced"])
        self.assertEqual(second["step"], 3)
        self.assertEqual(second["missed"], [])
        self.assertIn("Patient Approach", second["feedback"])
        self.assertIn("cervical-spine stabilization", second["feedback"])

    def test_chest_pain_scenario_can_complete(self):
        attempt_id = self.client.post("/api/scenarios/chest_pain/start/").json()["attempt_id"]
        scenario = SCENARIOS["chest_pain"]
        for step in scenario["steps"]:
            answer = ", ".join(aliases[0] for aliases in step["concepts"].values())
            body = self._respond(attempt_id, answer).json()
            self.assertTrue(body["advanced"])
        self.assertTrue(body["completed"])
        self.assertEqual(body["overall_score"], 100)
        self.assertTrue(TrainingAttempt.objects.get(public_id=attempt_id).completed)

    def test_rejects_blank_response(self):
        attempt_id = self.client.post("/api/scenarios/stroke/start/").json()["attempt_id"]
        response = self._respond(attempt_id, " ")
        self.assertEqual(response.status_code, 400)

    def test_attempt_transcript_requires_scoped_secret(self):
        started = self.client.post("/api/scenarios/stroke/start/").json()
        public_id = started["attempt_id"]
        token = started["attempt_token"]
        attacker = Client()

        self.assertEqual(attacker.get(f"/api/attempts/{public_id}/").status_code, 404)
        self.assertEqual(
            attacker.post(
                f"/api/attempts/{public_id}/respond/",
                data=json.dumps({"response": "equipment"}),
                content_type="application/json",
                HTTP_X_ATTEMPT_TOKEN="wrong-token",
            ).status_code,
            404,
        )
        authorized = attacker.get(
            f"/api/attempts/{public_id}/",
            HTTP_X_ATTEMPT_TOKEN=token,
        )
        self.assertEqual(authorized.status_code, 200)
        self.assertEqual(authorized["Cache-Control"], "no-store")

    def test_scenario_list_does_not_leak_other_users_progress(self):
        self.client.post("/api/scenarios/stroke/start/")
        scenarios = Client().get("/api/scenarios/").json()["scenarios"]
        self.assertTrue(all(not item["attempted"] for item in scenarios))
        self.assertTrue(all(item["score"] is None for item in scenarios))

    def test_security_headers_are_present(self):
        response = self.client.get("/")
        self.assertIn("default-src 'self'", response["Content-Security-Policy"])
        self.assertEqual(response["X-Frame-Options"], "DENY")
        self.assertEqual(response["X-Content-Type-Options"], "nosniff")
        self.assertIn("camera=()", response["Permissions-Policy"])

    def test_api_rejects_non_text_and_oversized_answers(self):
        started = self.client.post("/api/scenarios/stroke/start/").json()
        endpoint = f"/api/attempts/{started['attempt_id']}/respond/"
        headers = {"HTTP_X_ATTEMPT_TOKEN": started["attempt_token"]}
        non_text = self.client.post(
            endpoint,
            data=json.dumps({"response": ["not", "text"]}),
            content_type="application/json",
            **headers,
        )
        self.assertEqual(non_text.status_code, 400)
        too_long = self.client.post(
            endpoint,
            data=json.dumps({"response": "x" * 4001}),
            content_type="application/json",
            **headers,
        )
        self.assertEqual(too_long.status_code, 400)

    def test_privacy_and_terms_pages_are_public(self):
        self.assertContains(self.client.get("/privacy/"), "Do not enter real patient")
        self.assertContains(
            self.client.get("/terms/"), "independent educational application"
        )

    def test_public_branding_is_independent_and_hides_internal_protocol_metadata(self):
        homepage = self.client.get("/")
        self.assertContains(homepage, "Interactive EMT scenario training")
        self.assertNotContains(homepage, "Maryland protocol practice")

        payload = self.client.get("/api/scenarios/").json()
        self.assertIn("not affiliated with", payload["disclaimer"])
        self.assertTrue(payload["scenarios"])
        self.assertNotIn("protocol", payload["scenarios"][0])
