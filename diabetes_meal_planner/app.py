from flask import Flask, render_template, request, session
from flask_session import Session
from google import genai
import requests
import re
import os
from dotenv import load_dotenv  

load_dotenv()  

app = Flask(__name__)
app.secret_key = "your_secret_key"  
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))  

USDA_API_KEY = "EmvkrhGbWIFSkEFZVRlBPK46RFGUPEjZ20yhsi2C"  

def get_gemini_ai_response(meal_type, max_calories, max_sugar, min_fiber, min_protein):
    prompt = (
        f"Generate a structured list of {meal_type} meals based on these criteria: "
        f"Max Calories: {max_calories}, Max Sugar: {max_sugar}, "
        f"Min Fiber: {min_fiber}, Min Protein: {min_protein}. "
        f"Format the output as a visually appealing, well-structured HTML table with columns: "
        f"Meal Name, Ingredients, Calories, Sugar, Fiber, Protein, and Notes. "
        f"Ensure the table is properly colored and formatted for readability."

        f"\n\nAdditionally:\n"
        f"- Provide a **brief, engaging summary** about the importance of nutrition in maintaining a healthy lifestyle.\n"
        f"- Include a **motivational quote** related to health and well-being, styled elegantly with color and emphasis.\n"
        f"- Offer **three concise medical tips** relevant to healthy eating and balanced nutrition.\n"
        f"- Generate an elegant **flowchart** with title visually appealing with normal rectangles and horizontal directed arrow connections that visually guides users on making healthier meal choices based on their dietary goals.\n"
        f"- Provide **relevant links** to trusted resources for meal planning, nutritional guidelines, or dietary recommendations. No unwanted explanations at the end.\n"

        f"\n⚠ **Important Instructions:**\n"
        f"- Do **NOT** include unnecessary explanations or unrelated content.\n"
        f"- The response should be **highly structured, visually appealing, and medically useful**.\n"
        f"- Ensure all content is directly relevant to meal planning and healthy eating."
    )

    try:
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        formatted_response = format_response_as_html(response.text.strip())
        session["ai_response"] = formatted_response  # Store AI response in session
        return formatted_response
    except Exception as e:
        return f"<p class='text-danger'>Error: {str(e)}</p>"

def format_response_as_html(response_text):
    meals = re.findall(
        r"\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(.*?)\s*\|",
        response_text
    )

    if not meals:
        return f"<p>{response_text}</p>"

    table_html = """
    <table class='table table-bordered mt-3'>
        <thead class='table-dark'>
            <tr>
                <th>Meal Name</th>
                <th>Ingredients</th>
                <th>Calories</th>
                <th>Sugar (g)</th>
                <th>Fiber (g)</th>
                <th>Protein (g)</th>
                <th>Notes</th>
            </tr>
        </thead>
        <tbody>
    """

    for meal in meals:
        table_html += "<tr>" + "".join(f"<td>{col}</td>" for col in meal) + "</tr>"

    table_html += "</tbody></table>"
    return table_html

def get_nutrition_from_usda(food_name):
    url = f"https://api.nal.usda.gov/fdc/v1/foods/search?query={food_name}&api_key={USDA_API_KEY}"

    try:
        response = requests.get(url)
        data = response.json()

        if "foods" in data and len(data["foods"]) > 0:
            food_item = data["foods"][0]
            nutrients = {n["nutrientName"]: n["value"] for n in food_item.get("foodNutrients", [])}

            return {
                "Food": food_item.get("description", "Unknown"),
                "Calories": nutrients.get("Energy", "N/A"),
                "Protein": nutrients.get("Protein", "N/A"),
                "Carbohydrates": nutrients.get("Carbohydrate, by difference", "N/A"),
                "Sugar": nutrients.get("Sugars, total including NLEA", "N/A"),
                "Fiber": nutrients.get("Fiber, total dietary", "N/A"),
            }
        else:
            return {"Error": "No results found."}
    except Exception as e:
        return {"Error": str(e)}

@app.route("/", methods=["GET", "POST"])
def index():
    nutrition_data = None
    if request.method == "POST":
        if "food_name" in request.form:
            food_name = request.form["food_name"]
            nutrition_data = get_nutrition_from_usda(food_name)
        else:
            try:
                meal_type = request.form["meal_type"]
                max_calories = int(request.form["max_calories"])
                max_sugar = int(request.form["max_sugar"])
                min_fiber = int(request.form["min_fiber"])
                min_protein = int(request.form["min_protein"])

                session["ai_response"] = get_gemini_ai_response(meal_type, max_calories, max_sugar, min_fiber, min_protein)
            except ValueError:
                session["ai_response"] = "<p class='text-danger'>Please enter valid numeric values for calories, sugar, fiber, and protein.</p>"

    return render_template("index.html", ai_response=session.get("ai_response"), nutrition_data=nutrition_data)

if __name__ == "__main__":
    app.run(debug=True)
