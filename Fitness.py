import datetime
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import pprint

# Connect to the SQLite database
# Connect to the SQLite database
conn = sqlite3.connect('fitness_tracker.db')
cursor = conn.cursor()

# Create goals table with ISO 8601 date format
cursor.execute('''CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY,
                description TEXT,
                target INTEGER,
                deadline TEXT,
                progress INTEGER,
                username TEXT
                )''')

# Initial users dictionary
users = {
    'Bhushan61': 'Bhushan@61',
    'Pranav18': 'Pranav@18',
    'bh': '22'
}

# Function to handle user login
def login():
    print("\n** Enter Password to access the Premium Version of Fitness Tracker **\n")
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    
    # Verify username and password
    if username in users and users[username] == password:
        print("Login successful!\n")
        return username
    else:
        print("Invalid username or password. Please try again.")
        return None

# Define the Goal class for setting and tracking goals
class Goal:
    def __init__(self, description, target, deadline, username):
        self.description = description
        self.target = target
        self.deadline = deadline
        self.progress = 0
        self.username = username

    def update_progress(self, amount):
        self.progress += amount

    def is_complete(self):
        return self.progress >= self.target

    def days_remaining(self):
        return (self.deadline - datetime.date.today()).days

    def save_to_database(self):
        # Serialize deadline to ISO 8601 format
        iso_deadline = self.deadline.isoformat()
        cursor.execute("INSERT INTO goals (description, target, deadline, progress, username) VALUES (?, ?, ?, ?, ?)",
                       (self.description, self.target, iso_deadline, self.progress, self.username))
        conn.commit()
        self.id = cursor.lastrowid

    def update_progress_in_db(self):
        cursor.execute("UPDATE goals SET progress = ? WHERE id = ?", (self.progress, self.id))
        conn.commit()
   
# Define the ProgressTracker class for updating and displaying progress
class ProgressTracker:
    def update_progress(self, goal, amount):
        goal.update_progress(amount)
        goal.update_progress_in_db()
        print("Progress updated successfully!")

    def display_progress(self, goal):
        print("\nGoal: {}".format(goal.description))
        print("Target: {}".format(goal.target))
        print("Deadline: {}".format(goal.deadline))
        print("Progress: {}/{}".format(goal.progress, goal.target))
        print("Days remaining: {}".format(goal.days_remaining()))

# Define the Visualization class for generating a pie chart of goal progress
class Visualization:
    @staticmethod
    def generate_pie_chart(goal):
        # Calculate progress made and remaining progress
        progress_made = goal.progress
        remaining_progress = goal.target - progress_made

        # Pie chart labels and sizes
        labels = ['Progress Made', 'Remaining']
        sizes = [progress_made, remaining_progress]
        colors = ['green', 'red']

        # Create the pie chart
        plt.figure(figsize=(6, 6))
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%')
        plt.title('Goal Progress')
        plt.show()

# Function to calculate BMI and collect user data
def calculate_bmi():
    name = input("Enter your Name: ")
    try:
        age = int(input("Enter your Age in years: "))
        weight = float(input("Enter your Weight in Kg: "))
        height_cm = float(input("Enter your Height in centimeters: "))
    except ValueError:
        print("Invalid input. Please enter numeric values for age, weight, and height.")
        return None
    
    # Convert height from cm to meters
    height_meter = height_cm / 100
    
    # Calculate BMI
    bmi = weight / (height_meter ** 2)
    
    # Determine BMI category
    if bmi < 18.5:
        category = "Underweight"
    elif 18.5 <= bmi < 25:
        category = "Normal weight"
    elif 25 <= bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"
    
    # Display the result
    print(f"\nName: {name}")
    print(f"Age: {age} years")
    print(f"Weight: {weight} Kg")
    print(f"Height: {height_cm} cm")
    print(f"BMI: {bmi:.2f}")
    print(f"You are in the '{category}' category according to BMI.")
    
    # Return user data and BMI for further calculations
    return name, age, weight, height_cm, bmi

# Function to collect daily data for calorie intake and expenditure
def collect_daily_data():
    daily_data = []
    
    print("\n** Enter daily data **\n")
    while True:
        date = input("Enter the date (YYYY-MM-DD): ")
        try:
            calorie_intake = float(input("Enter daily calorie intake: "))
            calorie_expenditure = float(input("Enter daily calorie expenditure: "))
        except ValueError:
            print("Invalid input. Please enter numeric values for calorie intake and expenditure.")
            continue
        
        daily_data.append((date, calorie_intake, calorie_expenditure))
        
        more_data = input("Do you want to enter more data? (yes/no): ").lower()
        if more_data != 'yes':
            break
    
    return daily_data

# Function to plot the graph of daily calorie intake vs. expenditure
def plot_calorie_graph(daily_data):
    # Use Seaborn style for the graph
    sns.set(style="whitegrid")

    # Extract dates, calorie intake, and calorie expenditure from daily data
    dates = [data[0] for data in daily_data]
    calorie_intake = [data[1] for data in daily_data]
    calorie_expenditure = [data[2] for data in daily_data]

    # Create a figure and axis
    plt.figure(figsize=(12, 8))

    # Define bar width
    bar_width = 0.35

    # Plotting calorie intake and expenditure as side-by-side bars
    x = range(len(dates))
    intake_bars = plt.bar(x, calorie_intake, width=bar_width, label='Calorie Intake', color='#4caf50', alpha=0.8)
    expenditure_bars = plt.bar([i + bar_width for i in x], calorie_expenditure, width=bar_width, label='Calorie Expenditure', color='#ff5722', alpha=0.8)

    # Customize the x-tick labels to be centered between the two sets of bars
    plt.xticks([i + bar_width / 2 for i in x], dates)

    # Add gridlines for readability
    plt.grid(True, linestyle='--', alpha=0.7)

    # Customize labels and title
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Calories', fontsize=12)
    plt.title('Calorie Intake vs. Expenditure', fontsize=16)

    # Add a legend to differentiate between calorie intake and expenditure
    plt.legend(loc='best', fontsize=10)

    # Add data labels above the bars
    def add_labels(bars):
        for bar in bars:
            height = bar.get_height()
            plt.annotate(
                f'{height:.0f}',  # Format the label
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 5),  # Add some space above the bar
                textcoords="offset points",
                ha='center',
                fontsize=10
            )

    # Add data labels for both intake and expenditure bars
    add_labels(intake_bars)
    add_labels(expenditure_bars)

    # Display the graph
    plt.show()

# Function to suggest a 7-day diet plan based on user goals
def suggest_diet_plan():
    print("\n** Choose your diet goal **\n")
    print("1. Weight Gain")
    print("2. Weight Loss")
    print("3. Maintenance")  
    print("4. Muscle Gain")
    
    choice = input("Enter your choice: ")

    if choice == "1":
        print("\n** 7-Day Diet Plan for Weight Gain **\n")
        diet_plan = {
     "Day 1": {
        "Breakfast": "3 scrambled eggs with cheese and whole-grain bread (Approx. 500 calories) \n",
        "Mid_morning_snack": "Greek yogurt with honey and mixed nuts (Approx. 250 calories) ",
        "Lunch": "Chicken curry with rice, and a side of vegetables (Approx. 700 calories) \n",
        "Afternoon_snack": "Protein shake with banana and peanut butter (Approx. 300 calories)",
        "Dinner": "Beef stir-fry with rice and vegetables (Approx. 800 calories)",
        "Workout": "45 minutes of weightlifting"
    },
    "Day 2": {
        "breakfast": "Whole-grain pancakes with fruit and honey (Approx. 500 calories)",
        "mid_morning_snack": "Glass of milk with banana (Approx. 200 calories)",
        "lunch": "Grilled salmon with sweet potatoes and steamed veggies (Approx. 700 calories)",
        "afternoon_snack": "Handful of almonds (Approx. 200 calories)",
        "dinner": "Pasta with chicken and vegetables (Approx. 800 calories)",
        "workout": "45 minutes of HIIT"
    },
    "Day 3": {
        "breakfast": "Oatmeal with milk and fruit (Approx. 400 calories)",
        "mid_morning_snack": "Peanut butter toast (Approx. 300 calories)",
        "lunch": "Beef burger with whole-grain bun and sweet potato fries (Approx. 800 calories)",
        "afternoon_snack": "Greek yogurt with honey and berries (Approx. 200 calories)",
        "dinner": "Chicken curry with rice and mixed veggies (Approx. 800 calories)",
        "workout": "45 minutes of strength training"
    },
    "Day 4": {
        "breakfast": "Smoothie with milk, banana, and protein powder (Approx. 400 calories)",
        "mid_morning_snack": "Handful of trail mix (Approx. 300 calories)",
        "lunch": "Lentil soup with rice and vegetables (Approx. 700 calories)",
        "afternoon_snack": "Cheese and whole-grain crackers (Approx. 200 calories)",
        "dinner": "Grilled chicken with rice and mixed vegetables (Approx. 800 calories)",
        "workout": "45 minutes of swimming"
    },
    "Day 5": {
        "breakfast": "Omelette with cheese and vegetables, and whole-grain toast (Approx. 400 calories)",
        "mid_morning_snack": "Protein shake with fruit (Approx. 300 calories)",
        "lunch": "Grilled steak with mashed potatoes and veggies (Approx. 800 calories)",
        "afternoon_snack": "Fruit and nut bar (Approx. 200 calories)",
        "dinner": "Pasta with chicken, vegetables, and tomato sauce (Approx. 800 calories)",
        "workout": "45 minutes of HIIT"
    },
    "Day 6": {
        "breakfast": "French toast with syrup and fruit (Approx. 400 calories)",
        "mid_morning_snack": "Greek yogurt with honey and mixed nuts (Approx. 300 calories)",
        "lunch": "Beef stew with potatoes and vegetables (Approx. 800 calories)",
        "afternoon_snack": "Handful of almonds (Approx. 200 calories)",
        "dinner": "Shrimp stir-fry with rice and vegetables (Approx. 800 calories)",
        "workout": "45 minutes of cycling"
    },
    "Day 7": {
        "breakfast": "Whole-grain waffles with fruit and syrup (Approx. 500 calories)",
        "mid_morning_snack": "Protein bar (Approx. 250 calories)",
        "lunch": "Chicken fajitas with tortillas and vegetables (Approx. 800 calories)",
        "afternoon_snack": "Handful of trail mix (Approx. 300 calories)",
        "dinner": "Turkey and rice casserole with vegetables (Approx. 800 calories)",
        "workout": "45 minutes of strength training"
    }
}
    elif choice == "2":
        print("\n** 7-Day Diet Plan for Weight Loss **\n")
        diet_plan = {
         "Day 1": {
        "breakfast": "1 bowl of oatmeal with berries and almond milk (Approx. 300 calories)",
        "mid_morning_snack": "1 apple (Approx. 70 calories)",
        "lunch": "Grilled chicken salad with greens, tomatoes, and vinaigrette dressing (Approx. 400 calories)",
        "afternoon_snack": "Carrot sticks and hummus (Approx. 100 calories)",
        "dinner": "Grilled fish with steamed vegetables (Approx. 400 calories)",
        "workout": "45 minutes of brisk walking"
    },
    "Day 2": {
        "breakfast": "1 smoothie with spinach, banana, and protein powder (Approx. 300 calories)",
        "mid_morning_snack": "1 orange (Approx. 60 calories)",
        "lunch": "1 bowl of quinoa with black beans and vegetables (Approx. 400 calories)",
        "afternoon_snack": "Greek yogurt with berries (Approx. 150 calories)",
        "dinner": "Turkey stir-fry with vegetables (Approx. 400 calories)",
        "workout": "45 minutes of yoga"
    },
    "Day 3": {
        "breakfast": "2 boiled eggs with whole-grain toast (Approx. 300 calories)",
        "mid_morning_snack": "Handful of almonds (Approx. 100 calories)",
        "lunch": "Grilled shrimp with a mixed salad (Approx. 400 calories)",
        "afternoon_snack": "1 pear (Approx. 70 calories)",
        "dinner": "Chicken vegetable soup (Approx. 350 calories)",
        "workout": "45 minutes of cycling"
    },
    "Day 4": {
        "breakfast": "1 bowl of mixed fruit salad with yogurt (Approx. 250 calories)",
        "mid_morning_snack": "1 banana (Approx. 100 calories)",
        "lunch": "1 bowl of lentil soup with a side salad (Approx. 350 calories)",
        "afternoon_snack": "1 glass of green smoothie (Approx. 150 calories)",
        "dinner": "Grilled salmon with steamed vegetables (Approx. 400 calories)",
           "workout": "30 minutes of jogging"
    },
    "Day 5": {
        "breakfast": "2 boiled eggs with whole-grain toast and sliced tomato (Approx. 300 calories)",
        "mid_morning_snack": "1 glass of buttermilk (Approx. 60 calories)",
        "lunch": "1 bowl of chicken and vegetable stir-fry (Approx. 400 calories)",
        "afternoon_snack": "Celery sticks with peanut butter (Approx. 120 calories)",
        "dinner": "Grilled fish with asparagus (Approx. 400 calories)",
        "workout": "45 minutes of yoga"
    },
    "Day 6": {
        "breakfast": "1 smoothie with spinach, banana, and protein powder (Approx. 300 calories)",
        "mid_morning_snack": "1 apple (Approx. 70 calories)",
        "lunch": "Grilled chicken salad with mixed greens and vinaigrette (Approx. 400 calories)",
        "afternoon_snack": "Greek yogurt with honey (Approx. 120 calories)",
        "dinner": "Lentil soup with a side salad (Approx. 350 calories)",
        "workout": "45 minutes of brisk walking"
    },
    "Day 7": {
        "breakfast": "1 bowl of oats with berries and almond milk (Approx. 300 calories)",
        "mid_morning_snack": "Carrot sticks and hummus (Approx. 100 calories)",
        "lunch": "Grilled chicken wrap with whole-grain tortilla and vegetables (Approx. 400 calories)",
        "afternoon_snack": "Handful of almonds (Approx. 100 calories)",
        "dinner": "Shrimp stir-fry with steamed vegetables (Approx. 400 calories)",
        "workout": "30 minutes of dancing"
    }
}
    elif choice == "3":
        print("\n** 7-Day Diet Plan for Maintenance **\n")
        diet_plan = {
         "Day 1": {
        "breakfast": "1 bowl of oatmeal with milk and berries (Approx. 300 calories)",
        "mid_morning_snack": "Greek yogurt with honey (Approx. 150 calories)",
        "lunch": "Grilled chicken with whole-grain rice and vegetables (Approx. 550 calories)",
        "afternoon_snack": "1 apple (Approx. 70 calories)",
        "dinner": "Salmon with quinoa and vegetables (Approx. 500 calories)",
        "workout": "30 minutes of moderate-intensity exercise (e.g., walking, cycling)"
    },
    "Day 2": {
        "breakfast": "1 bowl of whole-grain cereal with milk and fruit (Approx. 300 calories)",
        "mid_morning_snack": "Handful of mixed nuts (Approx. 150 calories)",
        "lunch": "Turkey salad with mixed greens and vinaigrette dressing (Approx. 500 calories)",
        "afternoon_snack": "Greek yogurt with berries (Approx. 150 calories)",
        "dinner": "Chicken stir-fry with vegetables and brown rice (Approx. 500 calories)",
        "workout": "30 minutes of yoga"
    },
    "Day 3": {
        "breakfast": "Whole-grain toast with scrambled eggs and vegetables (Approx. 350 calories)",
        "mid_morning_snack": "1 pear (Approx. 70 calories)",
        "lunch": "Grilled fish with sweet potatoes and steamed veggies (Approx. 550 calories)",
        "afternoon_snack": "1 orange (Approx. 60 calories)",
        "dinner": "Chicken salad wrap with whole-grain tortilla and vegetables (Approx. 500 calories)",
        "workout": "30 minutes of brisk walking"
    },
    "Day 4": {
        "breakfast": "Smoothie with banana, spinach, and protein powder (Approx. 300 calories)",
        "mid_morning_snack": "1 orange (Approx. 60 calories)",
        "lunch": "Lentil soup with a side salad (Approx. 450 calories)",
        "afternoon_snack": "1 banana (Approx. 100 calories)",
        "dinner": "Grilled fish with steamed vegetables (Approx. 500 calories)",
        "workout": "30 minutes of swimming"
    },
    "Day 5": {
        "breakfast": "French toast with berries (Approx. 300 calories)",
        "mid_morning_snack": "Greek yogurt with honey and nuts (Approx. 200 calories)",
        "lunch": "Grilled steak with whole-grain rice and vegetables (Approx. 600 calories)",
        "afternoon_snack": "1 pear (Approx. 70 calories)",
        "dinner": "Pasta with chicken, vegetables, and tomato sauce (Approx. 500 calories)",
        "workout": "30 minutes of dancing"
    },
    "Day 6": {
        "breakfast": "Whole-grain pancakes with fruit and honey (Approx. 350 calories)",
        "mid_morning_snack": "Greek yogurt with berries (Approx. 150 calories)",
        "lunch": "Chicken salad wrap with whole-grain tortilla and vegetables (Approx. 500 calories)",
        "afternoon_snack": "Handful of mixed nuts (Approx. 150 calories)",
        "dinner": "Shrimp stir-fry with vegetables and quinoa (Approx. 500 calories)",
        "workout": "30 minutes of cycling"
    },
    "Day 7": {
        "breakfast": "1 bowl of oatmeal with almond milk and berries (Approx. 300 calories)",
        "mid_morning_snack": "1 apple (Approx. 70 calories)",
        "lunch": "Turkey salad with mixed greens and vinaigrette (Approx. 500 calories)",
        "afternoon_snack": "Carrot sticks and hummus (Approx. 100 calories)",
        "dinner": "Grilled chicken with rice and mixed vegetables (Approx. 500 calories)",
        "workout": "30 minutes of moderate-intensity exercise"
    }
}
    elif choice == "4":
        print("\n** 7-Day Diet Plan for Muscle Gain **\n")
        diet_plan = {
         "Day 1": {
        "breakfast": "4 scrambled eggs with cheese and whole-grain toast (Approx. 500 calories)",
        "mid_morning_snack": "Protein shake with fruit and peanut butter (Approx. 300 calories)",
        "lunch": "Grilled chicken breast with sweet potato and steamed veggies (Approx. 700 calories)",
        "afternoon_snack": "Greek yogurt with honey and berries (Approx. 250 calories)",
        "dinner": "Beef stir-fry with rice and mixed vegetables (Approx. 800 calories)",
        "workout": "1 hour of weightlifting"
    },
    "Day 2": {
        "breakfast": "Whole-grain pancakes with fruit and honey (Approx. 500 calories)",
        "mid_morning_snack": "Protein shake with banana and peanut butter (Approx. 300 calories)",
        "lunch": "Grilled salmon with sweet potatoes and steamed veggies (Approx. 700 calories)",
        "afternoon_snack": "Handful of almonds (Approx. 250 calories)",
        "dinner": "Pasta with chicken and vegetables (Approx. 800 calories)",
        "workout": "1 hour of strength training"
    },
    "Day 3": {
        "breakfast": "Oatmeal with milk and fruit (Approx. 400 calories)",
        "mid_morning_snack": "Greek yogurt with honey and mixed nuts (Approx. 300 calories)",
        "lunch": "Beef burger with whole-grain bun and sweet potato fries (Approx. 800 calories)",
        "afternoon_snack": "Handful of trail mix (Approx. 250 calories)",
        "dinner": "Chicken curry with rice and mixed veggies (Approx. 800 calories)",
        "workout": "1 hour of HIIT"
    },
    "Day 4": {
        "breakfast": "Smoothie with milk, banana, and protein powder (Approx. 400 calories)",
        "mid_morning_snack": "Peanut butter on whole-grain bread (Approx. 300 calories)",
        "lunch": "Lentil soup with rice and vegetables (Approx. 700 calories)",
        "afternoon_snack": "Cheese and whole-grain crackers (Approx. 250 calories)",
        "dinner": "Grilled chicken with rice and mixed vegetables (Approx. 800 calories)",
        "workout": "1 hour of weightlifting"
    },
    "Day 5": {
        "breakfast": "Omelette with cheese and vegetables and whole-grain toast (Approx. 400 calories)",
        "mid_morning_snack": "Protein shake with fruit and peanut butter (Approx. 300 calories)",
        "lunch": "Grilled steak with mashed potatoes and veggies (Approx. 800 calories)",
        "afternoon_snack": "Handful of mixed nuts (Approx. 250 calories)",
        "dinner": "Pasta with chicken, vegetables, and tomato sauce (Approx. 800 calories)",
        "workout": "1 hour of strength training"
    },
    "Day 6": {
        "breakfast": "French toast with syrup and fruit (Approx. 400 calories)",
        "mid_morning_snack": "Greek yogurt with honey and mixed nuts (Approx. 300 calories)",
        "lunch": "Beef stew with potatoes and vegetables (Approx. 800 calories)",
        "afternoon_snack": "Greek yogurt with honey and berries (Approx. 250 calories)",
        "dinner": "Shrimp stir-fry with rice and vegetables (Approx. 800 calories)",
        "workout": "1 hour of HIIT"
    },
    "Day 7": {
        "breakfast": "Whole-grain waffles with fruit and syrup (Approx. 500 calories)",
        "mid_morning_snack": "Protein bar (Approx. 250 calories)",
        "lunch": "Chicken fajitas with tortillas and vegetables (Approx. 800 calories)",
        "afternoon_snack": "Peanut butter on whole-grain bread (Approx. 300 calories)",
        "dinner": "Turkey and rice casserole with vegetables (Approx. 800 calories)",
        "workout": "1 hour of weightlifting"
}
}

    else:
        print("Invalid choice. Please try again.")
        return
    
    # Print the diet plan with proper formatting
    for day, plan in diet_plan.items():
       print(f"{day}:")
       for meal, description in plan.items():
          print(f"    {meal.capitalize()}:")
          print(f"        {description}")
       print("")  # Add a blank line after each day



# Function to set and track goals for the user
def set_and_track_goals(username):
    print("\n** Set and track goals **")
    
    try:
        # Get user input for the goal description, target, and deadline
        goal_description = input("Enter your goal description: ")
        target = int(input("Enter your target progress: "))
        deadline = input("Enter the deadline (YYYY-MM-DD): ")
        deadline = datetime.datetime.strptime(deadline, "%Y-%m-%d").date()
        
        # Create a new goal object and save it to the database
        goal = Goal(goal_description, target, deadline, username)
        goal.save_to_database()
        
        progress_tracker = ProgressTracker()
        
        # Main loop to track and update progress
        while not goal.is_complete() and goal.days_remaining() > 0:
            print("\nSelect an option:")
            print("1. Update progress")
            print("2. View progress")
            print("3. Visualize progress")
            print("4. Exit")
            
            choice = input("Enter your choice: ")
            
            if choice == "1":
                amount = int(input("Enter the amount of progress made: "))
                progress_tracker.update_progress(goal, amount)
            elif choice == "2":
                progress_tracker.display_progress(goal)
            elif choice == "3":
                Visualization.generate_pie_chart(goal)
            elif choice == "4":
                print("Exiting goal tracking...")
                break
            else:
                print("Invalid choice. Please try again.")
        
        # Final messages
        if goal.is_complete():
            print("Congratulations! You've achieved your goal!")
        elif goal.days_remaining() <= 0:
            print("Time's up! You didn't achieve your goal. Keep pushing!")
    except Exception as e:
        print(f"An error occurred while setting and tracking goals: {e}")
pprint.pprint(suggest_diet_plan, width=120)
        

# Main function to display the menu and handle user choices
def main():
    username = login()
    
    if username:
        while True:
            print("\n** Welcome to the Fitness Tracker **\n")
            print("1. Calculate BMI")
            print("2. Suggest Diet Plan")
            print("3. Collect Daily Data")
          
            print("4. Set and Track Goals")
            print("5. Exit")
            
            choice = input("Enter your choice: ")
            
            if choice == "1":
                calculate_bmi()
            elif choice == "2":
                suggest_diet_plan()
            elif choice == "3":
                daily_data = collect_daily_data()
                plot_calorie_graph(daily_data)
           
            elif choice == "4":
                set_and_track_goals(username)
            elif choice == "5":
                print("Thank you for using the Fitness Tracker. Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

# Run the program
if __name__== "__main__":
    main()