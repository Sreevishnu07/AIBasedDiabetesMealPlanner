// Dark Mode Toggle
const toggleButton = document.getElementById("darkModeToggle");
toggleButton.addEventListener("click", () => {
    document.body.classList.toggle("dark-mode");
});

// Form Submission Handler
document.getElementById("mealForm").addEventListener("submit", function(event) {
    event.preventDefault();

    // Get input values
    const mealType = document.getElementById("meal_type").value;
    const maxCalories = document.getElementById("max_calories").value;
    const maxSugar = document.getElementById("max_sugar").value;
    const minFiber = document.getElementById("min_fiber").value;
    const minProtein = document.getElementById("min_protein").value;

    // Simulated meal plan response (Replace with API Call)
    const sampleMeals = `
        <table>
            <tr>
                <th>Meal Name</th>
                <th>Ingredients</th>
                <th>Calories</th>
                <th>Sugar (g)</th>
                <th>Fiber (g)</th>
                <th>Protein (g)</th>
            </tr>
            <tr>
                <td>Oatmeal with Berries</td>
                <td>Oats, Almond Milk, Blueberries</td>
                <td>180</td>
                <td>5</td>
                <td>6</td>
                <td>7</td>
            </tr>
            <tr>
                <td>Greek Yogurt with Nuts</td>
                <td>Greek Yogurt, Almonds, Honey</td>
                <td>200</td>
                <td>8</td>
                <td>4</td>
                <td>10</td>
            </tr>
        </table>
    `;

    document.getElementById("mealResults").innerHTML = sampleMeals;
});
