
from precision_matching_engine import PrecisionMatchConfig, solve_weekly_matches

payload = {
    "cycleId": "2026w14",
    "algorithmVersion": "precision-v2.0.0",
    "participants": [
        {
            "userId": "u_1",
            "hardFilters": {
                "gender": "female",
                "sexuality": "heterosexual",
                "grade": 2,
                "campus": "main",
                "college": "business",
                "height": 165,
                "heightPrefMin": 170,
                "heightPrefMax": 190,
                "crossCampus": True,
                "sameCollege": True,
            },
            "status": {
                "verified": True,
                "completedQuestionnaire": True,
                "paused": False,
                "optIn": True,
            },
            "features": {
                "selfLikert": {
                    "marriage": 6,
                    "sleep": 5,
                    "ritual": 6,
                    "introvert": 4,
                    "logic_feel": 5,
                    "hustle": 6,
                    "drink": 2,
                    "smoke": 1,
                    "family_career": 5,
                    "conflict": 5,
                    "intimacy_pace": 4,
                    "opposite_friend": 3,
                },
                "spending": "flexible",
                "diet": "no_restriction",
                "studyspot": "library",
                "meet_freq": "medium",
                "interests": ["movie", "travel", "coffee"],
                "selfTraits": ["warm", "stable", "honest"],
            },
            "preferences": {
                "partnerPref": {
                    "hustle": 5,
                    "logic_feel": 4,
                    "introvert": 3,
                    "smoke": 1,
                    "drink": 2,
                    "appearance": 5,
                },
                "partnerTraits": ["honest", "stable"],
                "interestOverlap": "similar",
                "importantDimensions": ["marriage", "smoke", "drink", "hustle"],
                "partnerTraitsImportant": True,
            },
            "history": {
                "blockedUserIds": [],
                "matchedUserIds": [],
            },
        },
        {
            "userId": "u_2",
            "hardFilters": {
                "gender": "male",
                "sexuality": "heterosexual",
                "grade": 3,
                "campus": "main",
                "college": "engineering",
                "height": 178,
                "heightPrefMin": 155,
                "heightPrefMax": 170,
                "crossCampus": True,
                "sameCollege": True,
            },
            "status": {
                "verified": True,
                "completedQuestionnaire": True,
                "paused": False,
                "optIn": True,
            },
            "features": {
                "selfLikert": {
                    "marriage": 6,
                    "sleep": 4,
                    "ritual": 5,
                    "introvert": 3,
                    "logic_feel": 4,
                    "hustle": 6,
                    "drink": 2,
                    "smoke": 1,
                    "family_career": 5,
                    "conflict": 4,
                    "intimacy_pace": 4,
                    "opposite_friend": 4,
                },
                "spending": "flexible",
                "diet": "no_restriction",
                "studyspot": "library",
                "meet_freq": "medium",
                "interests": ["movie", "basketball", "coffee"],
                "selfTraits": ["stable", "honest", "active"],
            },
            "preferences": {
                "partnerPref": {
                    "hustle": 5,
                    "logic_feel": 5,
                    "introvert": 4,
                    "smoke": 1,
                    "drink": 2,
                    "appearance": 4,
                },
                "partnerTraits": ["warm", "honest"],
                "interestOverlap": "similar",
                "importantDimensions": ["marriage", "smoke", "drink"],
                "partnerTraitsImportant": True,
            },
            "history": {
                "blockedUserIds": [],
                "matchedUserIds": [],
            },
        },
    ],
}

config = PrecisionMatchConfig(
    candidate_threshold=0.57,
    reveal_threshold=0.68,
)

result = solve_weekly_matches(payload, config)

print(result["matches"])
print(result["unmatched"])
