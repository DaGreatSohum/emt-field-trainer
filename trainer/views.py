import json
import hashlib
import hmac
import os
import re
import secrets
import unicodedata
from datetime import timedelta
from difflib import SequenceMatcher

from django.core.cache import cache
from django.core.exceptions import RequestDataTooBig
from django.http import Http404, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from .chest_pain import CHEST_PAIN_SCENARIO
from .additional_scenarios import ADDITIONAL_SCENARIOS
from .models import TrainingAttempt
from .standard_steps import standardize_scenarios


SCENARIOS = {
    "chest_pain": {
        "title": "Chest Pain / ACS",
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
                    "You have a three-person BLS crew: you, your ambulance driver, and your partner. "
                    "What equipment do you plan on bringing to the scene?"
                ),
                "concepts": {
                    "BSI/PPE": ["ppe", "gloves", "eye protection", "bsi"],
                    "primary assessment bag": [
                        "first in bag", "first-in bag", "jump bag", "medical bag",
                        "stethoscope", "bp cuff", "blood pressure",
                    ],
                    "airway and oxygen equipment": [
                        "airway", "oxygen", "o2", "bvm", "bag valve", "nrb",
                        "nonrebreather", "nasal cannula",
                    ],
                    "AED/monitor": ["aed", "monitor", "defibrillator"],
                    "portable suction": ["suction"],
                    "medications": ["aspirin", "medication", "oral glucose"],
                },
                "critical": ["BSI/PPE", "airway and oxygen equipment", "AED/monitor"],
                "advance_always": True,
                "completion": (
                    "Thanks for your response. Equipment selections are not graded in this training "
                    "app. A recommended extensive list includes appropriate "
                    "BSI/PPE, a primary assessment bag with vital-sign equipment, airway and oxygen "
                    "equipment including a BVM, portable suction, an AED/monitor, and authorized BLS "
                    "medications such as aspirin."
                ),
            },
            {
                "prompt": (
                    "You arrive on scene at a two-story single-family home. "
                    "What are your first considerations?"
                ),
                "concepts": {
                    "BSI/PPE": ["bsi", "ppe", "gloves", "body substance"],
                    "scene safety": ["scene safe", "scene safety", "hazard", "safe"],
                    "number of patients": [
                        "number of patient", "number of pts", "how many patient", "how many pts",
                        "one patient", "1 patient", "only patient", "only pt",
                        "any other patient", "any other pts",
                    ],
                    "additional resources": [
                        "additional resource", "als", "engine", "paramedic",
                        "fire department", "request resource",
                    ],
                },
                "critical": ["BSI/PPE", "scene safety", "number of patients", "additional resources"],
                "first_hint": (
                    "Although that step might be important at another time, what should you consider now?"
                ),
                "second_hint": (
                    "Although that step might be important at another time, you want to conduct the "
                    "Scene Size-Up first. What should you consider in the Scene Size-Up?"
                ),
                "partial_hint": "What else is important for the Scene Size-Up?",
                "completion": (
                    "The complete scene size-up includes BSI/PPE, scene safety, number of patients, "
                    "and consideration of additional resources.\n\nThe scene is safe, you have one "
                    "patient, and gloves are appropriate."
                ),
                "resource_context": True,
            },
            {
                "prompt": (
                    "You approach the patient. A nature of illness of chest pain is apparent. Assume "
                    "there is no language barrier and no need for MCI procedures. You find a 62-year-old "
                    "man sitting upright on a couch. He is clutching his chest and appears pale and "
                    "sweaty. What is your response?"
                ),
                "concepts": {
                    "general impression": ["general impression", "appearance", "looks", "pale", "diaphoretic", "sweaty"],
                    "immediate life threats": ["life threat", "immediate threat", "abc", "airway", "breathing", "circulation"],
                    "critical instability": ["critically unstable", "unstable", "extremis", "risk for deterioration"],
                },
                "critical": ["general impression", "immediate life threats", "critical instability"],
                "first_hint": (
                    "Although that step might be important at another time, what should you consider now?"
                ),
                "partial_hint": "You identified {matched}. What else belongs in your rapid general impression?",
                "completion": (
                    "Assessing immediate life threats and whether the patient is critically unstable "
                    "happens while you rapidly form your general impression. Critical instability "
                    "includes new altered mental status, airway compromise, acute respiratory distress, "
                    "poor perfusion, or another finding suggesting imminent deterioration to cardiac arrest."
                ),
            },
            {
                "prompt": (
                    "You observe no immediate life threats and determine that the patient is not "
                    "critically unstable. What is your response?"
                ),
                "concepts": {
                    "mental status/AVPU": ["mental status", "avpu", "alert", "verbal", "painful", "unresponsive"],
                    "professional introduction": ["introduce", "hello", "fire department", "ems", "my name"],
                    "chief complaint": ["chief complaint", "what is wrong", "what's wrong", "issue today", "what happened"],
                },
                "critical": ["mental status/AVPU"],
                "first_hint": (
                    "Although that step might be important at another time, what should you consider now?"
                ),
                "partial_hint": "You identified {matched}. How can you assess this naturally while engaging the patient?",
                "completion": (
                    "Assessing mental status is the next step. Saying, \"Hello, I am with the Fire "
                    "Department. What is the issue today?\" professionally assesses alertness while "
                    "also beginning to identify the chief complaint and whether the airway is patent."
                ),
            },
            {
                "prompt": (
                    "The patient answers, \"Oh... my chest is hurting me.\" His answer is clear, loud, "
                    "and understandable. What three things should you assess, consider, and acknowledge "
                    "before moving on?"
                ),
                "concepts": {
                    "breathing adequacy": [
                        "adequate breathing", "breathing adequate", "respiratory rate",
                        "rate and quality", "work of breathing", "chest rise", "lung sound",
                    ],
                    "oxygen saturation": ["spo2", "oxygen saturation", "pulse oximeter", "pulse ox"],
                    "oxygen need": [
                        "oxygen if", "supplemental oxygen", "need oxygen", "titrate oxygen",
                        "less than 94", "hypoxia", "respiratory distress",
                    ],
                },
                "critical": ["breathing adequacy", "oxygen saturation", "oxygen need"],
                "first_hint": (
                    "Clear, loud speech tells you the airway is patent. What comes next in the initial assessment?"
                ),
                "partial_hint": "You identified {matched}. What else must you determine about breathing?",
                "completion": (
                    "A clear response supports a patent airway. Next, determine whether breathing is "
                    "adequate, obtain SpO2 with pulse oximetry, and decide whether oxygen is indicated. "
                    "For suspected angina/STEMI without respiratory distress, avoid routine high-flow "
                    "oxygen when SpO2 is 94% or greater."
                ),
            },
            {
                "prompt": (
                    "Breathing is adequate at 18/min, lungs are clear, and SpO2 is 97% on room air. "
                    "What do you assess next?"
                ),
                "concepts": {
                    "pulse": ["pulse", "heart rate", "rate and rhythm"],
                    "perfusion/skin": ["perfusion", "skin", "color", "temperature", "condition", "capillary"],
                    "major bleeding": ["major bleeding", "severe bleeding", "hemorrhage"],
                },
                "critical": ["pulse", "perfusion/skin", "major bleeding"],
                "first_hint": "You have completed airway and breathing. What is the next part of the initial assessment?",
                "partial_hint": "You identified {matched}. What else completes the circulation check?",
                "completion": (
                    "Assess circulation: check the pulse, evaluate perfusion including skin signs, and "
                    "look for major external bleeding. The patient has a rapid regular radial pulse, "
                    "pale cool diaphoretic skin, and no external bleeding."
                ),
            },
            {
                "prompt": (
                    "Your initial assessment is complete. What focused history, vital signs, and "
                    "time-sensitive cardiac actions will you perform now?"
                ),
                "concepts": {
                    "OPQRST/SAMPLE": ["opqrst", "sample", "onset", "provocation", "quality", "allerg", "medication", "history"],
                    "complete vital signs": ["vital", "blood pressure", "pulse", "spo2", "respiratory rate"],
                    "aspirin": ["aspirin", "324", "325", "chew"],
                    "12-lead/ALS": ["12 lead", "12-lead", "ekg", "ecg", "als", "paramedic"],
                },
                "critical": ["OPQRST/SAMPLE", "complete vital signs", "aspirin", "12-lead/ALS"],
                "first_hint": "Think about the secondary assessment and care for suspected ACS.",
                "partial_hint": "You identified {matched}. What other time-sensitive ACS actions are indicated?",
                "completion": (
                    "Obtain OPQRST/SAMPLE history and complete vital signs. Administer 324 mg or 325 mg "
                    "chewed aspirin if not already given and no contraindication is identified. Arrange "
                    "a 12-lead EKG as soon as possible, ideally within 10 minutes of contact with an "
                    "EKG-capable clinician, and use ALS resources as appropriate."
                ),
            },
            {
                "prompt": (
                    "The patient rates pressure-like pain 8/10 and has prescribed nitroglycerin. "
                    "His BP is 138/84 and pulse is 96. What must you verify before assisting?"
                ),
                "concepts": {
                    "prescription/right medication": ["prescribed", "prescription", "right patient", "right medication"],
                    "blood pressure and pulse": ["blood pressure", "bp", "systolic", "pulse", "heart rate"],
                    "PDE/PAH medication": ["viagra", "cialis", "levitra", "erectile", "pde", "revatio", "adcirca", "pulmonary hypertension"],
                    "dose/reassessment": ["0.4", "3-5", "three to five", "reassess", "maximum 3", "max 3"],
                },
                "critical": ["prescription/right medication", "blood pressure and pulse", "PDE/PAH medication"],
                "first_hint": "What contraindications and vital-sign limits apply to BLS-assisted nitroglycerin?",
                "partial_hint": "You identified {matched}. What remaining safety check is required?",
                "completion": (
                    "Confirm the medication is prescribed to the patient, verify BP is greater than "
                    "90 mmHg and pulse is 60-150/min, and exclude pulmonary-hypertension or erectile-"
                    "dysfunction medication within the past 48 hours. Assist with 0.4 mg SL and reassess; "
                    "it may be repeated every 3-5 minutes while criteria remain met, to three total doses."
                ),
            },
            {
                "prompt": (
                    "After initial treatment, the pain improves but persists. Describe your transport, "
                    "notification, monitoring, and reassessment plan."
                ),
                "concepts": {
                    "appropriate cardiac destination": ["cardiac center", "pci", "stemi center", "appropriate facility", "hospital"],
                    "prompt transport": ["rapid transport", "prompt transport", "priority transport", "transport"],
                    "prearrival notification": ["notify", "notification", "radio report", "prearrival", "hospital alert"],
                    "continuous monitoring/reassessment": ["monitor", "reassess", "repeat vital", "repeat assessment"],
                },
                "critical": ["prompt transport", "prearrival notification", "continuous monitoring/reassessment"],
                "first_hint": "Treatment continues during transport. What destination and communication priorities remain?",
                "partial_hint": "You identified {matched}. What else ensures safe continuity of care?",
                "completion": (
                    "Begin prompt transport to the appropriate receiving facility, provide an early "
                    "prearrival report and cardiac alert when indicated, continuously monitor the "
                    "patient, and repeat vital signs and focused assessments after interventions or "
                    "any change in condition."
                ),
            },
        ],
    },
    "breathing": {
        "title": "Difficulty Breathing",
        "category": "Respiratory",
        "difficulty": "Beginner",
        "protocol": "Maryland 6.1-A",
        "dispatch": "53-year-old patient with worsening shortness of breath and wheezing.",
        "steps": [
            {
                "prompt": "What equipment and initial scene considerations do you prepare?",
                "concepts": {
                    "PPE": ["ppe", "gloves", "bsi"],
                    "airway bag": ["airway", "bvm", "bag valve"],
                    "oxygen": ["oxygen", "o2"],
                    "suction": ["suction"],
                    "AED/monitor": ["aed", "monitor"],
                },
                "critical": ["airway bag", "oxygen"],
            },
            {
                "prompt": "The patient speaks in two-word sentences with diffuse wheezing. What is your assessment and treatment?",
                "concepts": {
                    "position and ABCs": ["position", "upright", "abc", "airway"],
                    "oxygen/titration": ["oxygen", "spo2", "saturation"],
                    "bronchodilator": ["albuterol", "inhaler", "nebulizer", "bronchodilator"],
                    "ALS": ["als", "paramedic"],
                    "ventilation readiness": ["bvm", "ventilat", "fatigue"],
                },
                "critical": ["oxygen/titration", "bronchodilator", "ventilation readiness"],
            },
            {
                "prompt": "Air movement is now poor and mental status is declining. What do you do next?",
                "concepts": {
                    "assist ventilation": ["bvm", "positive pressure", "assist ventilation"],
                    "high-priority transport": ["rapid transport", "priority", "transport"],
                    "continuous reassessment": ["reassess", "continuous", "capnography", "spo2"],
                    "ALS intercept": ["als", "intercept", "paramedic"],
                },
                "critical": ["assist ventilation", "high-priority transport"],
            },
        ],
    },
    "anaphylaxis": {
        "title": "Anaphylaxis",
        "category": "Medical",
        "difficulty": "Intermediate",
        "protocol": "Maryland 4.5-A",
        "dispatch": "Adult with hives, wheezing, and facial swelling after a bee sting.",
        "steps": [
            {
                "prompt": "Identify your immediate priorities and treatment.",
                "concepts": {
                    "airway/ABCs": ["airway", "abc", "breathing"],
                    "epinephrine": ["epinephrine", "epi", "auto injector"],
                    "oxygen": ["oxygen", "o2"],
                    "ALS": ["als", "paramedic"],
                    "remove exposure": ["remove", "stinger", "exposure"],
                },
                "critical": ["airway/ABCs", "epinephrine"],
            },
            {
                "prompt": "The patient remains hypotensive with persistent wheezing. What are your next actions?",
                "concepts": {
                    "continued ABC/shock care": [
                        "abc", "airway", "oxygen", "shock", "supine", "keep warm",
                    ],
                    "additional epinephrine within scope": [
                        "repeat epi", "second epi", "additional epinephrine",
                        "medical direction", "protocol", "als",
                    ],
                    "albuterol": ["albuterol", "nebulizer"],
                    "rapid transport": ["transport", "priority"],
                    "reassess": ["reassess", "vital"],
                },
                "critical": ["continued ABC/shock care", "rapid transport"],
            },
        ],
    },
    "hypoglycemia": {
        "title": "Hypoglycemia",
        "category": "Medical",
        "difficulty": "Beginner",
        "protocol": "Maryland 4.10",
        "dispatch": "Diabetic patient who is confused, sweaty, and behaving abnormally.",
        "steps": [
            {
                "prompt": "What is your assessment approach and first diagnostic check?",
                "concepts": {
                    "ABCs": ["abc", "airway", "breathing", "circulation"],
                    "glucose": ["glucose", "glucometer", "blood sugar", "bgl"],
                    "stroke screen": ["stroke", "neurologic"],
                    "history": ["sample", "insulin", "medication", "meal"],
                },
                "critical": ["ABCs", "glucose"],
            },
            {
                "prompt": "Blood glucose is 48 mg/dL and the patient can follow commands and swallow. Treat and reassess.",
                "concepts": {
                    "oral glucose": ["oral glucose", "glucose gel", "sugar"],
                    "airway safety": ["swallow", "airway", "aspiration"],
                    "repeat glucose": ["repeat glucose", "recheck", "reassess"],
                    "transport decision": ["transport", "medical control", "refusal"],
                },
                "critical": ["oral glucose", "airway safety", "repeat glucose"],
            },
        ],
    },
    "seizure": {
        "title": "Active Seizure",
        "category": "Neurologic",
        "difficulty": "Intermediate",
        "protocol": "Maryland 4.14-A",
        "dispatch": "Adult actively seizing in a crowded restaurant.",
        "steps": [
            {
                "prompt": "Describe scene management and immediate patient care.",
                "concepts": {
                    "protect from injury": ["protect", "clear area", "padding", "do not restrain"],
                    "airway/oxygen": ["airway", "oxygen", "suction", "bvm"],
                    "time seizure": ["time", "duration"],
                    "glucose": ["glucose", "blood sugar"],
                    "ALS": ["als", "paramedic"],
                },
                "critical": ["protect from injury", "airway/oxygen", "time seizure"],
            },
            {
                "prompt": "The seizure stops after four minutes. How do you manage the postictal phase?",
                "concepts": {
                    "recovery position": ["recovery position", "lateral", "side"],
                    "ABCs/reassess": ["abc", "reassess", "vital"],
                    "history": ["history", "medication", "witness", "sample"],
                    "transport": ["transport"],
                },
                "critical": ["recovery position", "ABCs/reassess"],
            },
        ],
    },
    "stroke": {
        "title": "Suspected Stroke",
        "category": "Neurologic",
        "difficulty": "Intermediate",
        "protocol": "Maryland 4.17",
        "dispatch": "71-year-old with sudden facial droop and slurred speech.",
        "steps": [
            {
                "prompt": "What focused assessment and time-sensitive information do you obtain?",
                "concepts": {
                    "ABCs": ["abc", "airway", "breathing"],
                    "stroke scale": ["stroke scale", "cincinnati", "lams", "face", "arm", "speech"],
                    "last known well": ["last known well", "last known normal", "onset"],
                    "glucose": ["glucose", "blood sugar"],
                    "anticoagulants": ["anticoagulant", "blood thinner"],
                },
                "critical": ["stroke scale", "last known well", "glucose"],
            },
            {
                "prompt": "The screen is positive and glucose is normal. State transport, notification, and reassessment priorities.",
                "concepts": {
                    "stroke center": ["stroke center", "lvo", "thrombectomy"],
                    "prearrival alert": ["notify", "stroke alert", "prearrival"],
                    "rapid transport": ["rapid transport", "do not delay", "priority"],
                    "reassess": ["reassess", "monitor", "vital"],
                },
                "critical": ["stroke center", "prearrival alert", "rapid transport"],
            },
        ],
    },
    "overdose": {
        "title": "Opioid Overdose",
        "category": "Toxicology",
        "difficulty": "Beginner",
        "protocol": "Maryland 7.6-A",
        "dispatch": "Unresponsive adult with slow, shallow respirations and drug paraphernalia nearby.",
        "steps": [
            {
                "prompt": "What are your scene and primary assessment priorities?",
                "concepts": {
                    "scene/PPE": ["scene safe", "ppe", "gloves", "needle"],
                    "airway": ["airway", "suction"],
                    "ventilation": ["bvm", "ventilat", "breathing"],
                    "pulse/AED": ["pulse", "aed", "cardiac arrest"],
                    "ALS": ["als", "paramedic"],
                },
                "critical": ["scene/PPE", "airway", "ventilation"],
            },
            {
                "prompt": "The patient has a pulse but breathes four times per minute. Treat and set the goal of care.",
                "concepts": {
                    "BVM first": ["bvm", "ventilat", "oxygen"],
                    "naloxone": ["naloxone", "narcan"],
                    "adequate breathing goal": ["breathing", "respiratory", "not full consciousness"],
                    "transport/reassess": ["transport", "reassess", "monitor"],
                },
                "critical": ["BVM first", "naloxone", "adequate breathing goal"],
            },
        ],
    },
    "burns": {
        "title": "Thermal Burns",
        "category": "Trauma",
        "difficulty": "Intermediate",
        "protocol": "Maryland 8.1",
        "dispatch": "Adult burned in a kitchen fire; flames are extinguished.",
        "steps": [
            {
                "prompt": "Explain scene safety, immediate care, and burn assessment.",
                "concepts": {
                    "stop burning": ["stop burning", "remove", "jewelry", "smoldering"],
                    "airway/inhalation": ["airway", "inhalation", "soot", "hoarse"],
                    "no ice/prevent hypothermia": [
                        "no ice", "do not use ice", "hypothermia", "remove wet clothing",
                        "dry patient", "keep warm",
                    ],
                    "depth/TBSA": ["depth", "tbsa", "rule of nines", "palmar"],
                    "sterile covering": ["sterile", "dry sheet", "cover"],
                },
                "critical": ["stop burning", "airway/inhalation", "no ice/prevent hypothermia"],
            },
            {
                "prompt": "You estimate 20% partial-thickness burns with facial involvement. What are your transport and ongoing-care priorities?",
                "concepts": {
                    "burn center": ["burn center", "specialty"],
                    "high priority": ["priority", "rapid transport"],
                    "oxygen/airway": ["oxygen", "airway", "bvm"],
                    "prevent hypothermia": ["warm", "hypothermia", "cover"],
                    "pain/reassess": ["pain", "reassess", "vital"],
                },
                "critical": ["burn center", "oxygen/airway", "prevent hypothermia"],
            },
        ],
    },
    "major_trauma": {
        "title": "Multiple / Severe Trauma",
        "category": "Trauma",
        "difficulty": "Advanced",
        "protocol": "Maryland 8.4-A",
        "dispatch": "High-speed vehicle collision with one adult patient and significant vehicle damage.",
        "steps": [
            {
                "prompt": (
                    "The vehicle is stabilized and you reach the patient. "
                    "Describe your immediate trauma assessment and priorities."
                ),
                "concepts": {
                    "scene safety/PPE": ["scene safety", "ppe", "traffic", "hazard"],
                    "mechanism/resources": ["mechanism", "moi", "extrication", "additional resource"],
                    "manual stabilization": ["c spine", "spinal", "manual stabilization"],
                    "massive hemorrhage": ["hemorrhage", "bleeding", "tourniquet"],
                    "ABCs": ["airway", "breathing", "circulation", "abc"],
                },
                "critical": ["massive hemorrhage", "ABCs"],
            },
            {
                "prompt": "The patient is pale, tachycardic, hypotensive, and has an unstable pelvis. State treatment and destination priorities.",
                "concepts": {
                    "shock care": ["shock", "oxygen", "keep warm"],
                    "pelvic binder": ["pelvic binder", "pelvic stabilization"],
                    "rapid trauma transport": ["trauma center", "rapid transport", "priority"],
                    "ALS": ["als", "paramedic"],
                    "reassessment": ["reassess", "vital", "monitor"],
                },
                "critical": ["shock care", "pelvic binder", "rapid trauma transport"],
            },
        ],
    },
    "cardiac_arrest": {
        "title": "Adult Cardiac Arrest",
        "category": "Cardiac",
        "difficulty": "Advanced",
        "protocol": "Maryland 3.4-A",
        "dispatch": "Adult collapsed at a gym; a bystander reports the patient is not breathing normally.",
        "steps": [
            {
                "prompt": "You reach the patient. Talk through your first minute of care.",
                "concepts": {
                    "check responsiveness/pulse": ["responsive", "pulse", "breathing", "10 seconds"],
                    "HPCPR": ["cpr", "compressions", "100", "120", "high quality"],
                    "AED": ["aed", "defibrillator", "pads"],
                    "ventilation": ["bvm", "ventilat", "oxygen"],
                    "team roles": ["roles", "rotate", "team"],
                },
                "critical": ["check responsiveness/pulse", "HPCPR", "AED"],
            },
            {
                "prompt": "The AED advises a shock. Describe the next cycle while minimizing interruptions.",
                "concepts": {
                    "clear/shock": ["clear", "shock"],
                    "immediate CPR": ["immediate cpr", "resume compressions", "2 minutes"],
                    "minimal pauses": [
                        "minimal", "less than 10", "under 10", "10 seconds",
                        "pause", "interrupt",
                    ],
                    "ALS": ["als", "paramedic"],
                    "reassess rhythm": ["rhythm", "aed analysis", "reassess"],
                },
                "critical": ["clear/shock", "immediate CPR", "minimal pauses"],
            },
        ],
    },
}

# The detailed, owner-authored Call 1 script supersedes the shorter seed scenario.
SCENARIOS["chest_pain"] = CHEST_PAIN_SCENARIO
SCENARIOS.update(ADDITIONAL_SCENARIOS)
standardize_scenarios(SCENARIOS)


def _scenario_summary(key, scenario, latest=None):
    return {
        "key": key,
        "title": scenario["title"],
        "category": scenario["category"],
        "difficulty": scenario["difficulty"],
        "attempted": bool(latest),
        "score": latest.score if latest else None,
        "completed": latest.completed if latest else False,
    }


def _json_body(request):
    try:
        return json.loads(request.body.decode("utf-8") or "{}")
    except (json.JSONDecodeError, UnicodeDecodeError, RequestDataTooBig):
        return None


def _client_ip(request):
    # REMOTE_ADDR is supplied by the trusted web server. Do not trust arbitrary
    # X-Forwarded-For values here.
    return request.META.get("REMOTE_ADDR", "unknown")


def _rate_limited(bucket, identifier, limit, window=60):
    key = f"rate:{bucket}:{identifier}"
    try:
        count = cache.incr(key)
    except ValueError:
        cache.set(key, 1, timeout=window)
        count = 1
    return count > limit


def _token_digest(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _authorized_attempt(request, public_id):
    token = request.headers.get("X-Attempt-Token") or request.COOKIES.get(
        "emt_attempt_token"
    )
    if not token or len(token) > 256:
        raise Http404
    try:
        attempt = TrainingAttempt.objects.get(public_id=public_id)
    except TrainingAttempt.DoesNotExist as exc:
        raise Http404 from exc
    if not hmac.compare_digest(attempt.access_token_hash, _token_digest(token)):
        raise Http404
    return attempt


def _normalized_tokens(text):
    normalized = unicodedata.normalize("NFKD", text.lower())
    normalized = normalized.replace("₂", "2")
    normalized = re.sub(r"\bp\s*([1-4])\b", r"priority \1", normalized)
    normalized = re.sub(r"\blife\s*threats?\b", "life threat", normalized)
    normalized = re.sub(r"\bpts?\b", "patient", normalized)
    normalized = re.sub(r"\bc[\s-]*spine\b", "cervical spine", normalized)
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    common_field_typos = {
        "sftey": "safety",
        "saftey": "safety",
        "sfate": "safety",
        "safey": "safety",
        "glvoes": "gloves",
        "additonal": "additional",
        "adittional": "additional",
        "oxyegn": "oxygen",
        "oxgyen": "oxygen",
        "oxgen": "oxygen",
        "patinet": "patient",
        "asses": "assess",
        "assesment": "assessment",
        "reasses": "reassess",
        "abcs": "abc",
    }
    return [common_field_typos.get(token, token) for token in normalized.split()]


def _token_matches(user_token, expected_token):
    if user_token == expected_token:
        return True
    if user_token.isdigit() or expected_token.isdigit():
        return False
    if min(len(user_token), len(expected_token)) < 4:
        return False
    # Allows common field-entry errors such as "saftey", "sftey", and "oxgyen"
    # while avoiding short-token collisions such as "bp" and "bpm".
    return SequenceMatcher(None, user_token, expected_token).ratio() >= 0.84


def _phrase_matches(user_tokens, alias):
    expected_tokens = _normalized_tokens(alias)
    if not expected_tokens:
        return False
    for start, user_token in enumerate(user_tokens):
        if not _token_matches(user_token, expected_tokens[0]):
            continue
        if (
            expected_tokens == ["pulse"]
            and start + 1 < len(user_tokens)
            and user_tokens[start + 1] in {"ox", "oximeter", "oximetry"}
        ):
            continue
        previous_match = start
        all_found = True
        for expected in expected_tokens[1:]:
            next_match = next(
                (
                    index
                    for index in range(
                        previous_match + 1,
                        min(previous_match + 5, len(user_tokens)),
                    )
                    if _token_matches(user_tokens[index], expected)
                ),
                None,
            )
            if next_match is None:
                all_found = False
                break
            previous_match = next_match
        if all_found:
            return True
    return False


def _match_concepts(text, concepts):
    user_tokens = _normalized_tokens(text)
    matched = [
        concept
        for concept, aliases in concepts.items()
        if any(_phrase_matches(user_tokens, alias) for alias in aliases)
    ]
    orientation_concept = "orientation/A&O x4"
    domains_concept = "person, place, time, and situation/event"
    if orientation_concept in concepts and domains_concept in concepts:
        token_set = set(user_tokens)
        domains = (
            token_set & {"person", "name", "identity", "who", "president"},
            token_set & {"place", "location", "located", "where", "hospital", "city"},
            token_set & {"time", "date", "day", "month", "year", "when"},
            token_set & {
                "situation", "event", "events", "happened", "incident",
                "occurred", "led",
            },
        )
        if all(domains):
            for concept in (orientation_concept, domains_concept):
                if concept not in matched:
                    matched.append(concept)
    return matched


def _context_hint(text, step):
    """Return a redirect only when the learner actually mentioned its subject."""
    for contextual in step.get("context_hints", []):
        if any(_phrase_matches(_normalized_tokens(text), alias) for alias in contextual["aliases"]):
            return contextual["feedback"]
    return None


def _overall_score(transcript):
    """Score each clinical phase once, using the learner's best cumulative result."""
    scores_by_step = {}
    for item in transcript:
        if not item.get("graded", True):
            continue
        scores_by_step[item["step"]] = max(
            item["score"], scores_by_step.get(item["step"], 0)
        )
    return round(sum(scores_by_step.values()) / len(scores_by_step)) if scores_by_step else 0


def _format_hint(template, matched):
    return template.format(matched=", ".join(matched)) if "{matched}" in template else template


def _completion_feedback(step, step_entries, missed):
    if step.get("completion"):
        feedback = step["completion"]
    elif missed:
        feedback = (
            "Let's review the expected actions before continuing: "
            + ", ".join(step["concepts"])
            + "."
        )
    else:
        feedback = "Complete response. You identified every expected action for this stage."
    if step.get("resource_context"):
        combined = " ".join(item["response"].lower() for item in step_entries)
        resources = []
        if "als" in combined or "paramedic" in combined:
            resources.append("ALS")
        if "engine" in combined or "fire department" in combined:
            resources.append("an engine")
        if resources:
            feedback += (
                "\n\nThe additional resource you requested ("
                + " and ".join(resources)
                + ") is en route and will arrive shortly."
            )
        else:
            feedback += (
                "\n\nYou can consider requesting additional resources at any point "
                "during the call. Let's continue."
            )
    return feedback


def scenario_list(request):
    scenarios = [
        _scenario_summary(key, scenario)
        for key, scenario in SCENARIOS.items()
    ]
    return JsonResponse(
        {
            "scenarios": scenarios,
            "disclaimer": "EMT Field Trainer is an independent educational application. It is not affiliated with, sponsored by, or endorsed by MIEMSS, the State of Maryland, or any EMS agency. Scenarios are independently authored for training purposes and are informed by publicly available EMS clinical guidance. This app is not intended for real-time patient care or as a substitute for official protocols, medical direction, or formal EMS training.",
        }
    )


def scenario_detail(request, scenario_key):
    scenario = SCENARIOS.get(scenario_key)
    if not scenario:
        return JsonResponse({"error": "Scenario not found."}, status=404)
    return JsonResponse(
        {
            **_scenario_summary(scenario_key, scenario),
            "dispatch": scenario["dispatch"],
            "total_steps": len(scenario["steps"]),
        }
    )


@csrf_exempt
def start_attempt(request, scenario_key):
    if request.method != "POST":
        return JsonResponse({"error": "POST required."}, status=405)
    scenario = SCENARIOS.get(scenario_key)
    if not scenario:
        return JsonResponse({"error": "Scenario not found."}, status=404)
    if _rate_limited("start", _client_ip(request), limit=30):
        return JsonResponse({"error": "Too many attempts. Try again shortly."}, status=429)
    retention_days = int(os.getenv("ATTEMPT_RETENTION_DAYS", "90"))
    TrainingAttempt.objects.filter(
        updated_at__lt=timezone.now() - timedelta(days=retention_days)
    ).delete()
    access_token = secrets.token_urlsafe(32)
    attempt = TrainingAttempt.objects.create(
        scenario_key=scenario_key,
        access_token_hash=_token_digest(access_token),
    )
    response = JsonResponse(
        {
            "attempt_id": str(attempt.public_id),
            "attempt_token": access_token,
            "dispatch": scenario["dispatch"],
            "prompt": scenario["steps"][0]["prompt"],
            "step": 1,
            "total_steps": len(scenario["steps"]),
        },
        status=201,
    )
    response["Cache-Control"] = "no-store"
    response.set_cookie(
        "emt_attempt_token",
        access_token,
        max_age=60 * 60 * 8,
        httponly=True,
        secure=request.is_secure(),
        samesite="Strict",
        path=f"/api/attempts/{attempt.public_id}/",
    )
    return response


@csrf_exempt
def respond(request, attempt_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST required."}, status=405)
    payload = _json_body(request)
    if payload is None:
        return JsonResponse({"error": "Invalid JSON."}, status=400)
    if not isinstance(payload.get("response"), str):
        return JsonResponse({"error": "Response must be text."}, status=400)
    answer = payload["response"].strip()
    if not answer:
        return JsonResponse({"error": "A response is required."}, status=400)
    if len(answer) > 4000:
        return JsonResponse({"error": "Response is too long (maximum 4,000 characters)."}, status=400)

    attempt = _authorized_attempt(request, attempt_id)
    if _rate_limited("respond", attempt.public_id, limit=120):
        return JsonResponse({"error": "Too many responses. Try again shortly."}, status=429)
    if attempt.completed:
        return JsonResponse({"error": "This attempt is already complete."}, status=409)
    scenario = SCENARIOS.get(attempt.scenario_key)
    if not scenario or attempt.current_step >= len(scenario["steps"]):
        return JsonResponse({"error": "Attempt state is invalid."}, status=409)

    step = scenario["steps"][attempt.current_step]
    transcript = list(attempt.transcript)
    step_number = attempt.current_step + 1
    prior_step_entries = [item for item in transcript if item["step"] == step_number]
    attempt_number = len(prior_step_entries) + 1
    newly_matched = _match_concepts(answer, step["concepts"])
    cumulative_matched = list(
        dict.fromkeys(
            concept
            for item in prior_step_entries
            for concept in item["matched"]
        )
    )
    for concept in newly_matched:
        if concept not in cumulative_matched:
            cumulative_matched.append(concept)
    required = step.get("required", step["critical"])
    critical_missed = [name for name in required if name not in cumulative_matched]
    all_missed = [name for name in step["concepts"] if name not in cumulative_matched]
    # User-facing "missed" items are graded requirements. Optional concepts are
    # retained separately for audit/teaching and never reported as failures.
    missed = list(critical_missed)
    graded = step.get("graded", True)
    minimum_matches = step.get("minimum_matches")
    if not graded:
        step_score = 0
    elif minimum_matches is not None:
        step_score = min(
            100,
            round(100 * len(cumulative_matched) / minimum_matches),
        )
    elif required:
        matched_required = [name for name in required if name in cumulative_matched]
        step_score = round(100 * len(matched_required) / len(required))
    else:
        step_score = 100
    meets_progression = (
        len(cumulative_matched) >= minimum_matches
        if minimum_matches is not None
        else not critical_missed
    )
    should_advance = (
        step.get("advance_always", False)
        or meets_progression
        or attempt_number >= step.get("max_attempts", 3)
    )
    transcript.append(
        {
            "step": step_number,
            "attempt": attempt_number,
            "prompt": step["prompt"],
            "response": answer,
            "matched": cumulative_matched,
            "newly_matched": newly_matched,
            "missed": missed,
            "optional_unmentioned": [
                name for name in all_missed if name not in critical_missed
            ],
            "score": step_score,
            "graded": graded,
            "advanced": should_advance,
        }
    )
    if should_advance:
        attempt.current_step += 1
    attempt.completed = should_advance and attempt.current_step >= len(scenario["steps"])
    attempt.score = _overall_score(transcript)
    attempt.transcript = transcript
    attempt.save()

    step_entries = prior_step_entries + [transcript[-1]]
    if should_advance:
        coaching = _completion_feedback(step, step_entries, missed)
    elif cumulative_matched:
        coaching = _format_hint(
            step.get(
                "partial_hint",
                "You identified {matched}. What else is important at this stage?",
            ),
            cumulative_matched,
        )
        if contextual_coaching := _context_hint(answer, step):
            coaching += f"\n\n{contextual_coaching}"
    elif contextual_coaching := _context_hint(answer, step):
        coaching = contextual_coaching
    elif attempt_number == 1:
        coaching = step.get(
            "first_hint",
            "Although that step might be important at another time, what should you consider now?",
        )
    else:
        coaching = step.get(
            "second_hint",
            "Review the current phase of the assessment before moving to later care. What belongs here?",
        )

    result = {
        "completed": attempt.completed,
        "advanced": should_advance,
        "attempt_number": attempt_number,
        "step_score": step_score if graded else None,
        "overall_score": attempt.score,
        "matched": cumulative_matched,
        "missed": missed,
        "critical_missed": critical_missed,
        "feedback": coaching,
    }
    if attempt.completed:
        result["evaluation"] = _evaluation(attempt.score)
        result["transcript"] = transcript
    else:
        next_prompt = scenario["steps"][attempt.current_step]["prompt"]
        result.update(
            {
                "prompt": next_prompt,
                "step": attempt.current_step + 1,
                "total_steps": len(scenario["steps"]),
            }
        )
    response = JsonResponse(result)
    response["Cache-Control"] = "no-store"
    return response


def attempt_detail(request, attempt_id):
    attempt = _authorized_attempt(request, attempt_id)
    response = JsonResponse(
        {
            "id": attempt.id,
            "scenario": attempt.scenario_key,
            "score": attempt.score,
            "completed": attempt.completed,
            "current_step": attempt.current_step,
            "transcript": attempt.transcript,
            "evaluation": _evaluation(attempt.score) if attempt.completed else None,
        }
    )
    response["Cache-Control"] = "no-store"
    return response


def _evaluation(score):
    if score >= 85:
        return "Excellent field readiness. Maintain this structured, safety-first approach."
    if score >= 70:
        return "Good performance. Review the missed actions before repeating the scenario."
    if score >= 50:
        return "Developing performance. Review the applicable assessment and treatment guidance, then repeat this scenario."
    return "Needs focused review. Study the applicable assessment and treatment guidance before another attempt."
