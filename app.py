from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
import google.generativeai as genai  # Fixed import
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Get secret key from .env file
app.secret_key = os.getenv('SECRET_KEY')

# Configure Gemini API using API key from .env file
try:
    api_key = os.getenv('API_KEY')
    if not api_key:
        raise ValueError("API_KEY not found in .env file")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')  # Using flash model for higher quotas
    print("✅ Gemini API configured successfully")
except Exception as e: 
    print(f"❌ Configuration error: {e}")
    model = None

def get_travel_recommendations(season, month):
    """Get AI-generated travel recommendations"""
    if not season and not month:
        return ""

    context = []
    if season:
        context.append(season)
    if month:
        context.append(f"month {month}")
    context_str = " ".join(context)

    prompt = f"""
    Provide exactly 3 recommendations for visiting Himachal Pradesh during {context_str}.
    Each recommendation must:
    - Be in bullet point format starting with hyphen
    - Contain location name followed by colon
    - Be under 40 words
    - Include a seasonal-specific activity
    
    After the recommendations, add exactly one safety tip starting with 'Safety:'

    Example format:
    - Manali: Enjoy snowy landscapes and skiing 
    - Shimla: Experience pleasant weather for sightseeing
    - Dharamshala: Visit peaceful monasteries
    Safety: Watch for icy roads
    """

    try:
        if not model:
            raise RuntimeError("AI model not configured")

        response = model.generate_content(prompt)
        print(f"✅ AI Response received: {response.text[:100]}...")  # Debug log
        return response.text.strip()
    except Exception as e:
        print(f"❌ AI Error: {e}")
        # Return fallback message
        return """- Manali: Popular hill station with adventure sports
            - Shimla: Scenic capital with colonial architecture
            - Dharamshala: Tibetan cultural hub with mountain views
            Safety: Check weather forecasts regularly"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get form data
        season = request.form.get('season', '').strip()
        month = request.form.get('month', '').strip()
        year = request.form.get('year', '').strip()
        date = request.form.get('date', '').strip()
        time = request.form.get('time', '').strip()

        print(f"📝 Form data received: season={season}, month={month}, year={year}, date={date}, time={time}")

        # Validate input
        if not any([season, month, year, date, time]):
            flash('❌ Please fill at least one field!', 'error')
            return redirect(url_for('index'))

        # Get recommendations
        recommendations = ""
        if season or month:
            print("🤖 Getting AI recommendations...")
            recommendations = get_travel_recommendations(season, month)
            print(f"📋 Recommendations: {recommendations}")

        return render_template(
            'success.html',
            season=season,
            month=month,
            year=year,
            date=date,
            time=time,
            recommendations=recommendations
        )

    return render_template('index.html')

# Add error handlers
@app.errorhandler(500)
def internal_error(error):
    return "Internal Server Error - Check console for details", 500

@app.errorhandler(404)
def not_found(error):
    return "Page not found", 404

if __name__ == '__main__':
    print("🚀 Starting Flask application...")
    # Check if environment variables are loaded
    if os.getenv('API_KEY') and os.getenv('SECRET_KEY'):
        print("✅ Environment variables loaded successfully")
    else:
        print("❌ Warning: Environment variables not found")
    
    app.run(debug=True, port=5000)