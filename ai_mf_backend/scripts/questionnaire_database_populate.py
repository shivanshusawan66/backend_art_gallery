import os
import sys
import django
from datetime import datetime
from django.db import transaction

sys.path.append(rf"{os.getcwd()}")

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "ai_mf_backend.config.v1.django_settings"
)  # Use your project’s settings path

# Set up Django after setting environment variables
django.setup()

from ai_mf_backend.models.v1.database.questions import (
    Section,
    Question,
    Allowed_Response,
    ConditionalQuestion,
)


# Clear existing data
def clear_tables():
    """Clear existing data from all relevant tables."""
    Section.objects.all().delete()
    Question.objects.all().delete()
    Allowed_Response.objects.all().delete()
    ConditionalQuestion.objects.all().delete()
    print("Existing data cleared successfully.")


# Function to populate the section, question, and allowed_response tables
def populate_data(data):
    section_id_mapping = {
        "Experience Level": 10,
        "Risk Tolerance": 20,
        "Investment Duration": 30,
        "Decision Making Style": 40,
        "Emotional Reactions to Market Changes": 50,
        "Research and Professional Advice": 60,
        "Sectoral and Investment Preferences": 70,
    }

    base_question_id_mapping = {
        "Experience Level": 1000,
        "Risk Tolerance": 2000,
        "Investment Duration": 3000,
        "Decision Making Style": 4000,
        "Emotional Reactions to Market Changes": 5000,
        "Research and Professional Advice": 6000,
        "Sectoral and Investment Preferences": 7000,
    }

    with transaction.atomic():
        for section_name, questions_list in data.items():
            section_id = section_id_mapping.get(section_name)
            base_question_id = base_question_id_mapping.get(section_name)

            # Insert Section
            section = Section.objects.create(id=section_id, section=section_name)

            # Insert Questions and Allowed Responses
            for index, question_info in enumerate(questions_list):
                question_id = base_question_id + index + 1
                question = Question.objects.create(
                    id=question_id,
                    section=section,
                    question=question_info["question_text"],
                )

                for response_text in question_info["responses"]:
                    Allowed_Response.objects.create(
                        question=question, section=section, response=response_text
                    )
        print("Sections, questions, and allowed responses populated successfully.")


# Function to populate conditional_question table
def populate_conditional_questions(conditional_questions):
    section_map = {
        "Experience Level": 10,
        "Risk Tolerance": 20,
        "Decision Making Style": 40,
        "Emotional Reactions to Market Changes": 50,
    }

    with transaction.atomic():
        for section, questions in conditional_questions.items():
            section_id = section_map.get(section)

            for question_data in questions:
                dependent_question_id = question_data["question_id"]
                condition_question_ids = question_data["conditional"][
                    "condition_question"
                ]
                condition_answers = question_data["conditional"]["condition_answer"]

                if not isinstance(condition_question_ids, list):
                    condition_question_ids = [condition_question_ids]

                for condition_question_id in condition_question_ids:
                    allowed_responses = Allowed_Response.objects.filter(
                        question_id=condition_question_id
                    )

                    response_id_map = {
                        index + 1: response.id
                        for index, response in enumerate(allowed_responses)
                    }

                    for position, response_id in response_id_map.items():
                        visibility = "show" if position in condition_answers else "hide"

                        ConditionalQuestion.objects.create(
                            question_id=condition_question_id,
                            dependent_question_id=dependent_question_id,
                            response_id=response_id,
                            visibility=visibility,
                            add_date=datetime.now(),
                            update_date=datetime.now(),
                        )
        print("Conditional questions populated successfully.")


# Main function to orchestrate the population process
def main(data, conditional_questions):
    try:
        clear_tables()

        # Populate section, question, allowed_response
        populate_data(data)

        # Populate conditional_question table
        populate_conditional_questions(conditional_questions)

    except Exception as e:
        print(f"An error occurred: {e}")


data = {
    "Experience Level": [
        {
            "question_id": 1001,
            "question_text": "What is the value of your current holdings in Shares?",
            "responses": [
                "I am first time investor",
                "Less than INR 50,000",
                "INR 50,000 – INR 200,000",
                "INR 200,000 – INR 500,000",
                "More than INR 500,000",
            ],
        },
        {
            "question_id": 1002,
            "question_text": "What is the value of your current holdings in Mutual Funds? ",
            "responses": [
                "I am first time investor",
                "Less than INR 50,000",
                "INR 50,000 – INR 200,000",
                "INR 200,000 – INR 500,000",
                "More than INR 500,000",
            ],
        },
        {
            "question_id": 1003,
            "question_text": "How many active SIP investments are you doing currently?",
            "responses": ["1-3", "4-7", "7 - 10", "More than 10"],
            "conditional": {
                "condition_question": 1002,
                "condition_answer": [2, 3, 4, 5],
            },  # Show if response to 1002 is not (1)
        },
        {
            "question_id": 1004,
            "question_text": "What is the average frequency of your SIPs?",
            "responses": ["Quarterly", "Monthly", "Fortnightly", "Weekly"],
            "conditional": {
                "condition_question": 1002,
                "condition_answer": [2, 3, 4, 5],
            },  # Show if response to 1002 is not (1)
        },
        {
            "question_id": 1005,
            "question_text": "How often do you rebalance your Mutual Funds portfolio?",
            "responses": [
                "I don’t rebalance",
                "Once every six months",
                "Once every year",
                "Once every two years",
            ],
            "conditional": {
                "condition_question": 1002,
                "condition_answer": [2, 3, 4, 5],
            },  # Show if response to 1002 is not (1)
        },
        {
            "question_id": 1006,
            "question_text": "How often do you rebalance your Shares portfolio?",
            "responses": [
                "I don’t rebalance",
                "Once every month",
                "Once every quarter",
                "Once every six months",
                "Once every year",
            ],
            "conditional": {
                "condition_question": 1001,
                "condition_answer": [2, 3, 4, 5],
            },  # Show if response to 1001 is not (1)
        },
    ],
    "Risk Tolerance": [
        {
            "question_id": 2001,
            "question_text": "How often do you check your Shares portfolio?",
            "responses": [
                "Daily",
                "Once every week",
                "Once every month",
                "Once every quarter",
                "Once every six months",
            ],
            "conditional": {
                "condition_question": 1001,
                "condition_answer": [2, 3, 4, 5],
            },  # Show if response to 1001 is not (1)
        },
        {
            "question_id": 2002,
            "question_text": "How often do you check your Mutual Funds portfolio?",
            "responses": [
                "Once every week",
                "Once every month",
                "Once every quarter",
                "Once every six months",
                "Once every year",
            ],
            "conditional": {
                "condition_question": 1002,
                "condition_answer": [2, 3, 4, 5],
            },  # Show if response to 1002 is not (1)
        },
        {
            "question_id": 2003,
            "question_text": "How do you typically feel about taking financial risks?",
            "responses": [
                "I avoid risks at all costs",
                "I am willing to take moderate risks",
                "I enjoy taking high risks for potential higher rewards",
            ],
        },
        {
            "question_id": 2004,
            "question_text": "If your investment loses more than 10% in a month, how do you respond?",
            "responses": [
                "Sell immediately to cut further losses",
                "Wait and monitor the situation",
                "Buy more since the price is lower",
            ],
            "conditional": {
                "condition_question": [1001, 1002],
                "condition_answer": [2, 3, 4, 5],
            },  # Show if both 1001 and 1002 are not (1)
        },
        {
            "question_id": 2005,
            "question_text": "How important is it for you to protect your initial investment capital?",
            "responses": [
                "Extremely important",
                "Moderately important",
                "Not important, I’m focused on growth",
            ],
        },
        {
            "question_id": 2006,
            "question_text": "How much financial loss could you tolerate in a year?",
            "responses": [
                "None, I cannot afford to lose money",
                "I could tolerate some loss (up to 10%)",
                "I could tolerate significant losses (over 15%) if the long-term outlook is positive",
            ],
        },
        {
            "question_id": 2007,
            "question_text": "How much of your total wealth do you feel comfortable investing in high-risk assets?",
            "responses": ["0-10%", "10-30%", "30-50%"],
        },
        {
            "question_id": 2008,
            "question_text": "How much fluctuation are you willing to accept in your portfolio value?",
            "responses": [
                "Minimal fluctuation",
                "Moderate fluctuation",
                "High fluctuation, as long as long-term returns are maximized",
            ],
        },
        {
            "question_id": 2009,
            "question_text": "How much returns do you expect when investing?",
            "responses": [
                "Low Returns; I prefer investing in Low Risk funds to avoid big losses",
                "Moderate Returns; I prefer investing in Moderate Risk funds to balance risk and profits",
                "High Return; I prefer investing in High Risk funds to make more profits",
            ],
        },
    ],
    "Investment Duration": [
        {
            "question_id": 3001,
            "question_text": "What is the purpose of your investment?",
            "responses": ["Capital preservation", "Steady income", "Long-term growth"],
        },
        {
            "question_id": 3002,
            "question_text": "What is your primary financial goal for investing in mutual funds?",
            "responses": [
                "Generating regular income",
                "Preserving capital",
                "Funding a major expense (e.g., wedding, home, car)",
                "Building wealth over time",
                "Saving for retirement",
            ],
        },
        {
            "question_id": 3003,
            "question_text": "How long are you planning to stay invested before you may need to access your funds?",
            "responses": ["1-3 years", "3-7 years", "Over 7 years"],
        },
        {
            "question_id": 3004,
            "question_text": "How important is it for your investments to generate immediate returns?",
            "responses": [
                "Very important – I need quick returns",
                "Somewhat important – I want results within a few years",
                "Not important – I’m investing for the long term",
            ],
        },
    ],
    "Decision Making Style": [
        {
            "question_id": 4001,
            "question_text": "How often do you make investment decisions based on 'gut feeling' rather than analysis?",
            "responses": ["Frequently", "Occasionally", "Rarely"],
        },
        {
            "question_id": 4002,
            "question_text": "Do you tend to follow investment trends or advice from friends and family?",
            "responses": [
                "Yes, I follow others’ advice often",
                "Sometimes, if their ideas make sense",
                "No, I prefer to make my own decisions based on research",
            ],
        },
        {
            "question_id": 4003,
            "question_text": "How often do you look at past performance when selecting an investment?",
            "responses": [
                "Always, it’s my main criterion",
                "Sometimes, but I consider other factors too",
                "Rarely, I focus on future potential",
            ],
            "conditional": {
                "condition_question": [1001, 1002],
                "condition_answer": [2, 3, 4, 5],
            },  # Show if both 1001 and 1002 are not (1)
        },
        {
            "question_id": 4004,
            "question_text": "Do you find it hard to sell an underperforming investment after the intended holding period?",
            "responses": [
                "Yes, I often hold onto investments longer than I should",
                "Sometimes, but I try to be rational about it",
                "No, I sell if it doesn’t meet my expectations",
            ],
        },
        {
            "question_id": 4005,
            "question_text": "Which statement best describes your attitude toward past investment decisions?",
            "responses": [
                "I often regret past decisions and think about what I could’ve done differently.",
                "I sometimes question my choices but move on quickly.",
                "I rarely think about past decisions, focusing on future opportunities.",
                "I feel confident that my past decisions were the best at that time.",
            ],
        },
        {
            "question_id": 4006,
            "question_text": "How do you handle uncertainty or lack of information when making a decision?",
            "responses": [
                "I avoid making decisions until I have all the information.",
                "I tend to procrastinate until it feels urgent.",
                "I take action based on available information and intuition.",
                "I seek advice from experts or trusted sources before acting.",
            ],
        },
        {
            "question_id": 4007,
            "question_text": "Do you consider yourself more of a spender or a saver in general?",
            "responses": [
                "I’m more of a spender – I enjoy using my money now.",
                "I’m a balanced spender and saver.",
                "I’m more of a saver – I prioritize long-term goals over immediate spending.",
            ],
        },
    ],
    "Emotional Reactions to Market Changes": [
        {
            "question_id": 5001,
            "question_text": "How do you react when the stock market becomes volatile?",
            "responses": [
                "I become anxious and consider selling my investments.",
                "I remain calm but monitor my portfolio more closely.",
                "I am not concerned about short-term volatility.",
            ],
            "conditional": {
                "condition_question": [1001, 1002],
                "condition_answer": [2, 3, 4, 5],
            },
        },
        {
            "question_id": 5002,
            "question_text": "Do you find yourself frequently checking your investments during market downturns?",
            "responses": [
                "Yes, I check multiple times a day.",
                "Occasionally, when I see a significant drop.",
                "No, I stick to my long-term strategy.",
            ],
            "conditional": {
                "condition_question": [1001, 1002],
                "condition_answer": [2, 3, 4, 5],
            },
        },
        {
            "question_id": 5003,
            "question_text": "How would you feel if your portfolio underperforms compared to others?",
            "responses": [
                "Upset and likely to change my strategy.",
                "Curious but not overly concerned.",
                "Indifferent, as long as I’m meeting my own goals.",
            ],
        },
        {
            "question_id": 5004,
            "question_text": "If the media reports a potential market crash, what are you most likely to do?",
            "responses": [
                "Panic and sell my investments.",
                "Research further and decide based on the data.",
                "Ignore the news and stay on course.",
            ],
        },
        {
            "question_id": 5005,
            "question_text": "How do you typically feel when making investment decisions?",
            "responses": [
                "Anxious or stressed.",
                "Cautiously optimistic.",
                "Confident and clear-headed.",
                "Indifferent or neutral.",
            ],
        },
        {
            "question_id": 5006,
            "question_text": "How important is it for your investment to adapt to current economic conditions (e.g., inflation, recession, sectoral bets)?",
            "responses": [
                "Very important – I adjust my portfolio frequently as per economic conditions.",
                "Somewhat important – I make occasional adjustments.",
                "Not important – I stick with my long-term plan regardless of the economy.",
            ],
        },
    ],
    "Research and Professional Advice": [
        {
            "question_id": 6001,
            "question_text": "When making an investment decision, how much time do you spend on research?",
            "responses": [
                "Minimal, I make decisions quickly.",
                "Moderate, I spend some time researching.",
                "A lot, I thoroughly analyze all available information.",
            ],
        },
        {
            "question_id": 6002,
            "question_text": "Do you prefer to make investment decisions on your own or with guidance from an advisor or platform?",
            "responses": [
                "I prefer making decisions on my own.",
                "I seek guidance but make the final decision.",
                "I prefer relying entirely on an advisor or automated system.",
            ],
        },
        {
            "question_id": 6003,
            "question_text": "When making an investment decision, what are you likely to rely on the most? (Select all that apply)",
            "responses": [
                "Recommendations from friends and family.",
                "Gut feeling or intuition.",
                "News and Market Trends.",
                "My own research and analysis.",
                "Professional advice or recommendations.",
                "Data-driven analytical platforms like Fund Street.",
            ],
        },
        {
            "question_id": 6004,
            "question_text": "When you encounter conflicting advice from different sources, what do you typically do?",
            "responses": [
                "Follow the advice of a trusted advisor.",
                "Compare the advice and make an informed decision.",
                "Ignore the conflicting advice and follow my initial plan.",
            ],
        },
    ],
    "Sectoral and Investment Preferences": [
        {
            "question_id": 7001,
            "question_text": "How important is it for your portfolio to align with certain values (e.g., ESG, ethical investing)?",
            "responses": [
                "Very important.",
                "Somewhat important.",
                "Not important, I focus on returns.",
            ],
        },
        {
            "question_id": 7002,
            "question_text": "What sectors do you think will grow immensely in the future? (Select all that apply)",
            "responses": [
                "Clean Energy/Electric Vehicles.",
                "Traditional Energy (Oil/Gas).",
                "Internet Businesses/Online Platforms/Tech.",
                "Electronics/Semiconductor.",
                "Financial Markets/FinTech.",
                "Auto.",
                "Consumer Products.",
                "Healthcare.",
                "Biotech.",
                "Others (Provide Textbox input).",
            ],
        },
        {
            "question_id": 7003,
            "question_text": "What is your preference regarding expense ratio on funds?",
            "responses": [
                "Regular Funds (High expense ratio).",
                "Direct Funds (Moderate expense ratio).",
                "Index Funds (Low expense ratio).",
            ],
        },
        {
            "question_id": 7004,
            "question_text": "What is your benchmark preference?",
            "responses": [
                "Nifty 50.",
                "Sensex.",
                "Nifty Next 50.",
                "Nifty 200.",
                "Other.",
            ],
        },
        {
            "question_id": 7005,
            "question_text": "What is your preferred minimum rating for mutual funds?",
            "responses": ["1 Star.", "2 Star.", "3 Star.", "4 Star.", "5 Star."],
        },
        {
            "question_id": 7006,
            "question_text": "What is your fund house preference?",
            "responses": ["Top-Rated Only.", "Well-Known Brands.", "Any."],
        },
        {
            "question_id": 7007,
            "question_text": "What type of fund would you prefer?",
            "responses": [
                "Large Cap.",
                "Mid Cap.",
                "Small Cap.",
                "Debt.",
                "Hybrid.",
                "Index Funds.",
            ],
        },
        {
            "question_id": 7008,
            "question_text": "After a successful investment (e.g., high returns), how do you typically react?",
            "responses": [
                "I continue investing in a similar manner.",
                "I reduce my investments to lock in gains.",
                "I take on higher risks to maximize further gains.",
            ],
        },
    ],
}


conditional_questions = {
    "Experience Level": [
        {
            "question_id": 1003,
            "question_text": "How many active SIP investments are you doing currently?",
            "responses": ["1-3", "4-7", "7 - 10", "More than 10"],
            "conditional": {
                "condition_question": 1002,
                "condition_answer": [2, 3, 4, 5],
            },  # Show if response to 1002 is not (1)
        },
        {
            "question_id": 1004,
            "question_text": "What is the average frequency of your SIPs?",
            "responses": ["Quarterly", "Monthly", "Fortnightly", "Weekly"],
            "conditional": {
                "condition_question": 1002,
                "condition_answer": [2, 3, 4, 5],
            },  # Show if response to 1002 is not (1)
        },
        {
            "question_id": 1005,
            "question_text": "How often do you rebalance your Mutual Funds portfolio?",
            "responses": [
                "I don’t rebalance",
                "Once every six months",
                "Once every year",
                "Once every two years",
            ],
            "conditional": {
                "condition_question": 1002,
                "condition_answer": [2, 3, 4, 5],
            },  # Show if response to 1002 is not (1)
        },
        {
            "question_id": 1006,
            "question_text": "How often do you rebalance your Shares portfolio?",
            "responses": [
                "I don’t rebalance",
                "Once every month",
                "Once every quarter",
                "Once every six months",
                "Once every year",
            ],
            "conditional": {
                "condition_question": 1001,
                "condition_answer": [2, 3, 4, 5],
            },  # Show if response to 1001 is not (1)
        },
    ],
    "Risk Tolerance": [
        {
            "question_id": 2001,
            "question_text": "How often do you check your Shares portfolio?",
            "responses": [
                "Daily",
                "Once every week",
                "Once every month",
                "Once every quarter",
                "Once every six months",
            ],
            "conditional": {
                "condition_question": 1001,
                "condition_answer": [2, 3, 4, 5],
            },  # Show if response to 1001 is not (1)
        },
        {
            "question_id": 2002,
            "question_text": "How often do you check your Mutual Funds portfolio?",
            "responses": [
                "Once every week",
                "Once every month",
                "Once every quarter",
                "Once every six months",
                "Once every year",
            ],
            "conditional": {
                "condition_question": 1002,
                "condition_answer": [2, 3, 4, 5],
            },  # Show if response to 1002 is not (1)
        },
        {
            "question_id": 2004,
            "question_text": "If your investment loses more than 10% in a month, how do you respond?",
            "responses": [
                "Sell immediately to cut further losses",
                "Wait and monitor the situation",
                "Buy more since the price is lower",
            ],
            "conditional": {
                "condition_question": [1001, 1002],
                "condition_answer": [2, 3, 4, 5],
            },  # Show if both 1001 and 1002 are not (1)
        },
    ],
    "Decision Making Style": [
        {
            "question_id": 4003,
            "question_text": "How often do you look at past performance when selecting an investment?",
            "responses": [
                "Always, it’s my main criterion",
                "Sometimes, but I consider other factors too",
                "Rarely, I focus on future potential",
            ],
            "conditional": {
                "condition_question": [1001, 1002],
                "condition_answer": [2, 3, 4, 5],
            },  # Show if both 1001 and 1002 are not (1)
        }
    ],
    "Emotional Reactions to Market Changes": [
        {
            "question_id": 5001,
            "question_text": "How do you react when the stock market becomes volatile?",
            "responses": [
                "I become anxious and consider selling my investments.",
                "I remain calm but monitor my portfolio more closely.",
                "I am not concerned about short-term volatility.",
            ],
            "conditional": {
                "condition_question": [1001, 1002],
                "condition_answer": [2, 3, 4, 5],
            },  # Show if both 1001 and 1002 are not (1)
        },
        {
            "question_id": 5002,
            "question_text": "Do you find yourself frequently checking your investments during market downturns?",
            "responses": [
                "Yes, I check multiple times a day.",
                "Occasionally, when I see a significant drop.",
                "No, I stick to my long-term strategy.",
            ],
            "conditional": {
                "condition_question": [1001, 1002],
                "condition_answer": [2, 3, 4, 5],
            },  # Show if both 1001 and 1002 are not (1)
        },
    ],
}

if __name__ == "__main__":
    main(data, conditional_questions)
