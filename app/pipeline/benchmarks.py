"""
Benchmark roles, candidates, evidence chains, and gap strategies for BridgeIQ Employer View.
Directly aligns with Claude Employer Prototype and Swedish JobTech Taxonomy concepts.
"""

from typing import Any, Dict, List, Optional


def compute_candidate_composite(cov: float, sem: float) -> float:
    """Deterministic composite score: 60% competence coverage + 40% semantic fit."""
    return round(0.60 * cov + 0.40 * sem, 4)


def is_hidden_gem(cov: float, tsim: float) -> bool:
    """
    Identifies cross-domain 'Hidden Gems':
    High verified competence overlap (>= 75%) combined with low title similarity (< 45%),
    which causes traditional keyword-based ATS to discard the candidate.
    """
    return cov >= 0.75 and tsim < 0.45


BENCHMARK_ROLES: List[Dict[str, Any]] = [
    {
        "id": "job-077",
        "title": "Reliability Engineer, Industrial IoT",
        "employer": "Nordvik Automation AB",
        "location": "Västerås",
        "sector": "Industrial Tech & IoT",
        "reqs": [
            "Hög tillgänglighet",
            "Distribuerade system",
            "Incidenthantering",
            "Linux",
            "NIS2-direktivet",
        ],
        "cands": [
            {
                "alias": "Candidate 042 (Amara)",
                "raw_alias": "Candidate 042",
                "headline": "Senior Core Network Engineer (Telecom)",
                "years": 10,
                "cov": 0.85,
                "sem": 0.78,
                "tsim": 0.21,
                "summary": "Ten years running carrier-grade packet core at five-nines (99.999%) availability maps directly to the uptime and incident-response needs of this role.",
                "story": "Telecom core-network reliability → industrial IoT uptime",
                "evidence": [
                    {
                        "concept": "Hög tillgänglighet",
                        "jd": "Du ansvarar för driftsäkerhet och tillgänglighet i våra IoT-plattformar.",
                        "jdEn": "You own reliability and availability of our IoT platforms.",
                        "hidden": True,
                        "cv": "Kept a national 4G/5G packet core at 99.999% uptime for six years across multi-region infrastructure.",
                        "why": "Five-nines on national critical infrastructure exceeds the platform uptime target.",
                    },
                    {
                        "concept": "Distribuerade system",
                        "jd": "Erfarenhet av distribuerade system i produktion.",
                        "jdEn": "Experience with distributed systems in production.",
                        "hidden": False,
                        "cv": "Operated geo-redundant core clusters across three data centres with automated failover.",
                        "why": "Geo-redundant clustering is distributed systems work in production.",
                    },
                    {
                        "concept": "Incidenthantering",
                        "jd": "Du leder incidenthantering och rotorsaksanalys.",
                        "jdEn": "You lead incident management and root-cause analysis.",
                        "hidden": False,
                        "cv": "Led the 24/7 on-call rotation and authored root-cause post-mortems for major network outages.",
                        "why": "Has led exactly this process under strict telecom SLAs.",
                    },
                ],
                "gaps": [
                    {
                        "label": "NIS2-direktivet",
                        "effort": "days",
                        "strategy": "Complete a 2-day NIS2 regulatory workshop and map past telecom security compliance audits to NIS2 articles.",
                    }
                ],
            },
            {
                "alias": "Candidate 017",
                "raw_alias": "Candidate 017",
                "headline": "IoT Reliability Engineer",
                "years": 5,
                "cov": 0.80,
                "sem": 0.88,
                "tsim": 0.92,
                "summary": "A conventional match: five years running IoT fleets with strong Linux and monitoring skills, lighter on leading major incidents.",
                "story": "IoT reliability → IoT reliability (same domain)",
                "evidence": [
                    {
                        "concept": "Hög tillgänglighet",
                        "jd": "Du ansvarar för driftsäkerhet och tillgänglighet i våra IoT-plattformar.",
                        "jdEn": "You own reliability and availability of our IoT platforms.",
                        "hidden": False,
                        "cv": "Kept a 40,000-device sensor fleet above 99.9% availability.",
                        "why": "Directly the same responsibility at a comparable scale.",
                    },
                    {
                        "concept": "Linux",
                        "jd": "God vana av Linux i produktionsmiljö.",
                        "jdEn": "Solid experience with Linux in production.",
                        "hidden": False,
                        "cv": "Maintained embedded Linux images and OTA updates for edge gateways.",
                        "why": "Hands-on production Linux on edge hardware.",
                    },
                    {
                        "concept": "Distribuerade system",
                        "jd": "Erfarenhet av distribuerade system i produktion.",
                        "jdEn": "Experience with distributed systems in production.",
                        "hidden": False,
                        "cv": "Operated an MQTT broker cluster across two regions.",
                        "why": "Multi-region messaging is a distributed production system.",
                    },
                ],
                "gaps": [
                    {
                        "label": "Incidenthantering",
                        "effort": "weeks",
                        "strategy": "Shadow the on-call lead for two incident reviews and take ownership of one post-mortem.",
                    }
                ],
            },
            {
                "alias": "Candidate 088",
                "raw_alias": "Candidate 088",
                "headline": "Wind Turbine Service Technician",
                "years": 7,
                "cov": 0.76,
                "sem": 0.70,
                "tsim": 0.30,
                "summary": "Seven years keeping remote turbines online through SCADA monitoring and fast fault response, with practical Linux scripting.",
                "story": "Wind-farm uptime → connected-factory uptime",
                "evidence": [
                    {
                        "concept": "Hög tillgänglighet",
                        "jd": "Du ansvarar för driftsäkerhet och tillgänglighet i våra IoT-plattformar.",
                        "jdEn": "You own reliability and availability of our IoT platforms.",
                        "hidden": True,
                        "cv": "Raised turbine availability from 94% to 98.5% across a 60-unit offshore park.",
                        "why": "Measured, sustained availability gains on connected industrial assets.",
                    },
                    {
                        "concept": "Incidenthantering",
                        "jd": "Du leder incidenthantering och rotorsaksanalys.",
                        "jdEn": "You lead incident management and root-cause analysis.",
                        "hidden": False,
                        "cv": "Ran fault triage for SCADA alarms and logged root causes in the CMMS.",
                        "why": "Structured triage and root-cause logging on live alarms.",
                    },
                    {
                        "concept": "Linux",
                        "jd": "God vana av Linux i produktionsmiljö.",
                        "jdEn": "Solid experience with Linux in production.",
                        "hidden": False,
                        "cv": "Wrote Bash scripts to pull logs from turbine controllers running Linux.",
                        "why": "Practical production Linux, though at script level.",
                    },
                ],
                "gaps": [
                    {
                        "label": "Distribuerade system",
                        "effort": "months",
                        "strategy": "Complete a cloud fundamentals certification and build a small two-node monitoring setup as a portfolio piece.",
                    }
                ],
            },
        ],
    },
    {
        "id": "job-012",
        "title": "OT Security Specialist",
        "employer": "Kraftlinje Energi AB",
        "location": "Luleå",
        "sector": "Energy & Critical Infrastructure",
        "reqs": [
            "Informationssäkerhet",
            "Nätverkssäkerhet",
            "Industriella styrsystem",
            "Riskanalys",
            "NIS2-direktivet",
        ],
        "cands": [
            {
                "alias": "Candidate 063",
                "raw_alias": "Candidate 063",
                "headline": "Signals Officer (Armed Forces)",
                "years": 9,
                "cov": 0.82,
                "sem": 0.74,
                "tsim": 0.18,
                "summary": "Nine years securing field communication networks under formal military risk frameworks; strong fit for protecting critical energy infrastructure.",
                "story": "Military communications security → energy-grid OT security",
                "evidence": [
                    {
                        "concept": "Nätverkssäkerhet",
                        "jd": "Du säkrar nätverk mellan kontrollrum och ställverk.",
                        "jdEn": "You secure networks between control rooms and substations.",
                        "hidden": True,
                        "cv": "Designed and hardened encrypted radio and IP links for brigade command posts.",
                        "why": "Securing links between command sites and the field is the exact same topological pattern.",
                    },
                    {
                        "concept": "Riskanalys",
                        "jd": "Du genomför riskanalyser enligt etablerade ramverk.",
                        "jdEn": "You run risk assessments using established frameworks.",
                        "hidden": False,
                        "cv": "Produced formal threat and risk assessments before every deployment.",
                        "why": "Regular, framework-based risk assessment is routine work for them.",
                    },
                    {
                        "concept": "Informationssäkerhet",
                        "jd": "Erfarenhet av ledningssystem för informationssäkerhet.",
                        "jdEn": "Experience with information security management systems.",
                        "hidden": False,
                        "cv": "Owned classified-information handling procedures for a 300-person unit.",
                        "why": "Ran an information-security regime with audits and procedures.",
                    },
                ],
                "gaps": [
                    {
                        "label": "Industriella styrsystem",
                        "effort": "weeks",
                        "strategy": "Complete an IEC 62443 introduction and a hands-on PLC security lab.",
                    }
                ],
            },
            {
                "alias": "Candidate 029",
                "raw_alias": "Candidate 029",
                "headline": "Cybersecurity Analyst",
                "years": 4,
                "cov": 0.70,
                "sem": 0.86,
                "tsim": 0.81,
                "summary": "Four years in IT security operations; solid on network security and ISMS, new to industrial control systems and risk ownership.",
                "story": "IT SOC analyst → OT security",
                "evidence": [
                    {
                        "concept": "Nätverkssäkerhet",
                        "jd": "Du säkrar nätverk mellan kontrollrum och ställverk.",
                        "jdEn": "You secure networks between control rooms and substations.",
                        "hidden": False,
                        "cv": "Tuned firewall and IDS rules for a 2,000-user corporate network.",
                        "why": "Relevant network defence, though in an IT setting.",
                    },
                    {
                        "concept": "Informationssäkerhet",
                        "jd": "Erfarenhet av ledningssystem för informationssäkerhet.",
                        "jdEn": "Experience with information security management systems.",
                        "hidden": False,
                        "cv": "Supported ISO 27001 certification evidence collection.",
                        "why": "Direct ISMS experience.",
                    },
                    {
                        "concept": "NIS2-direktivet",
                        "jd": "Kunskap om NIS2 och krav på samhällsviktig verksamhet.",
                        "jdEn": "Knowledge of NIS2 and requirements on essential services.",
                        "hidden": False,
                        "cv": "Mapped company controls to NIS2 requirements in a gap assessment.",
                        "why": "Already applied NIS2 in practice.",
                    },
                ],
                "gaps": [
                    {
                        "label": "Industriella styrsystem",
                        "effort": "weeks",
                        "strategy": "Take a SCADA fundamentals course and visit a substation with the OT team in the first month.",
                    },
                    {
                        "label": "Riskanalys",
                        "effort": "weeks",
                        "strategy": "Lead one risk assessment end to end with a senior reviewer.",
                    },
                ],
            },
            {
                "alias": "Candidate 051 (Samira)",
                "raw_alias": "Candidate 051",
                "headline": "Railway Signalling Engineer",
                "years": 8,
                "cov": 0.78,
                "sem": 0.69,
                "tsim": 0.27,
                "summary": "Eight years on safety-critical signalling systems with formal hazard analysis; knows industrial control networks from the inside.",
                "story": "Rail signalling safety → grid control-system security",
                "evidence": [
                    {
                        "concept": "Industriella styrsystem",
                        "jd": "Erfarenhet av SCADA- och styrsystem.",
                        "jdEn": "Experience with SCADA and control systems.",
                        "hidden": False,
                        "cv": "Commissioned interlocking controllers and their SCADA supervision for 14 stations.",
                        "why": "Hands-on with industrial control systems in critical infrastructure.",
                    },
                    {
                        "concept": "Riskanalys",
                        "jd": "Du genomför riskanalyser enligt etablerade ramverk.",
                        "jdEn": "You run risk assessments using established frameworks.",
                        "hidden": False,
                        "cv": "Wrote hazard logs and risk assessments to EN 50126 for every railway signalling change.",
                        "why": "Formal, standards-based risk analysis on safety-critical systems.",
                    },
                    {
                        "concept": "Nätverkssäkerhet",
                        "jd": "Du säkrar nätverk mellan kontrollrum och ställverk.",
                        "jdEn": "You secure networks between control rooms and substations.",
                        "hidden": True,
                        "cv": "Segmented the signalling network from the station IT network.",
                        "why": "Network segmentation between control and IT is core OT security.",
                    },
                ],
                "gaps": [
                    {
                        "label": "NIS2-direktivet",
                        "effort": "days",
                        "strategy": "Complete a short NIS2 course and note how rail safety audits map directly to NIS2 obligations.",
                    }
                ],
            },
        ],
    },
    {
        "id": "job-150",
        "title": "Production Planner",
        "employer": "Ståhlberg Components AB",
        "location": "Jönköping",
        "sector": "Manufacturing & Logistics",
        "reqs": [
            "Produktionsplanering",
            "Lagerstyrning",
            "Affärssystem (ERP)",
            "Lean",
            "Leverantörskontakter",
        ],
        "cands": [
            {
                "alias": "Candidate 036",
                "raw_alias": "Candidate 036",
                "headline": "Production Planner",
                "years": 3,
                "cov": 0.74,
                "sem": 0.84,
                "tsim": 0.97,
                "summary": "Three years planning a single assembly line in ERP; a safe, conventional match with limited Lean and supplier experience.",
                "story": "Production planning → production planning (same field)",
                "evidence": [
                    {
                        "concept": "Produktionsplanering",
                        "jd": "Du planerar produktionen för tre monteringslinor.",
                        "jdEn": "You plan production for three assembly lines.",
                        "hidden": False,
                        "cv": "Planned weekly schedules for one assembly line of 40 operators.",
                        "why": "Same task, smaller scope.",
                    },
                    {
                        "concept": "Affärssystem (ERP)",
                        "jd": "Van användare av affärssystem, gärna SAP.",
                        "jdEn": "Experienced ERP user, preferably SAP.",
                        "hidden": False,
                        "cv": "Daily planning in SAP PP, including MRP runs.",
                        "why": "Direct SAP planning experience.",
                    },
                    {
                        "concept": "Lagerstyrning",
                        "jd": "Du optimerar lagernivåer och materialflöde.",
                        "jdEn": "You optimise stock levels and material flow.",
                        "hidden": False,
                        "cv": "Adjusted safety stock levels for 120 components.",
                        "why": "Hands-on inventory control.",
                    },
                ],
                "gaps": [
                    {
                        "label": "Lean",
                        "effort": "weeks",
                        "strategy": "Take a Lean Green Belt course and run one improvement project in the first quarter.",
                    }
                ],
            },
            {
                "alias": "Candidate 091",
                "raw_alias": "Candidate 091",
                "headline": "Humanitarian Logistics Coordinator",
                "years": 6,
                "cov": 0.81,
                "sem": 0.76,
                "tsim": 0.33,
                "summary": "Six years planning supply flows under tight constraints, with ERP-based stock control and a large supplier network.",
                "story": "Humanitarian supply chains → factory material planning",
                "evidence": [
                    {
                        "concept": "Lagerstyrning",
                        "jd": "Du optimerar lagernivåer och materialflöde.",
                        "jdEn": "You optimise stock levels and material flow.",
                        "hidden": True,
                        "cv": "Managed stock for four regional warehouses and cut stock-outs by 35%.",
                        "why": "Measured inventory optimisation across several sites.",
                    },
                    {
                        "concept": "Leverantörskontakter",
                        "jd": "Du har löpande kontakt med leverantörer.",
                        "jdEn": "You are in regular contact with suppliers.",
                        "hidden": False,
                        "cv": "Negotiated delivery schedules with 60+ suppliers across three countries.",
                        "why": "Supplier coordination at larger scale than the role needs.",
                    },
                    {
                        "concept": "Affärssystem (ERP)",
                        "jd": "Van användare av affärssystem, gärna SAP.",
                        "jdEn": "Experienced ERP user, preferably SAP.",
                        "hidden": False,
                        "cv": "Ran purchasing and stock reports in Microsoft Dynamics 365.",
                        "why": "Solid ERP use; SAP specifics can be learned quickly.",
                    },
                ],
                "gaps": [
                    {
                        "label": "Produktionsplanering",
                        "effort": "weeks",
                        "strategy": "Shadow the line planners for two weeks and complete a SAP PP basics course.",
                    }
                ],
            },
            {
                "alias": "Candidate 074 (Marcus)",
                "raw_alias": "Candidate 074",
                "headline": "Restaurant Operations Manager",
                "years": 8,
                "cov": 0.79,
                "sem": 0.72,
                "tsim": 0.12,
                "summary": "Eight years running high-volume kitchens: daily capacity planning, waste reduction and supplier management that transfer directly to a production floor.",
                "story": "Kitchen operations → factory production planning",
                "evidence": [
                    {
                        "concept": "Produktionsplanering",
                        "jd": "Du planerar produktionen för tre monteringslinor.",
                        "jdEn": "You plan production for three assembly lines.",
                        "hidden": True,
                        "cv": "Planned daily prep and staffing for three kitchens serving 1,200 covers.",
                        "why": "Capacity and sequence planning across three parallel lines.",
                    },
                    {
                        "concept": "Lean",
                        "jd": "Du driver förbättringsarbete enligt Lean.",
                        "jdEn": "You drive Lean improvement work.",
                        "hidden": True,
                        "cv": "Cut food waste by 28% by redesigning prep flow and batch sizes.",
                        "why": "Flow redesign and batch sizing are Lean in practice.",
                    },
                    {
                        "concept": "Leverantörskontakter",
                        "jd": "Du har löpande kontakt med leverantörer.",
                        "jdEn": "You are in regular contact with suppliers.",
                        "hidden": False,
                        "cv": "Managed 25 suppliers and renegotiated delivery windows.",
                        "why": "Ongoing supplier management with measurable results.",
                    },
                ],
                "gaps": [
                    {
                        "label": "Affärssystem (ERP)",
                        "effort": "weeks",
                        "strategy": "Complete a SAP introduction course and practise MRP runs in a sandbox.",
                    }
                ],
            },
        ],
    },
]


def get_benchmark_role(job_id: str) -> Optional[Dict[str, Any]]:
    """Lookup a benchmark role by id."""
    for role in BENCHMARK_ROLES:
        if role["id"] == job_id:
            return role
    return None


def list_benchmark_roles() -> List[Dict[str, Any]]:
    """Return all benchmark roles."""
    return BENCHMARK_ROLES
