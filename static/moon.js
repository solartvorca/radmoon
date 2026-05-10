document.addEventListener("DOMContentLoaded", function() {
    const moonPhaseDiv = document.querySelector(".moon-phase");
    const currentLunarDay = parseInt(moonPhaseDiv.querySelector("p").textContent.split(": ")[1]);

    const totalDays = 28;
    const phase = (currentLunarDay - 1) / totalDays; // 0 to 1

    // This is a very simplistic representation. A real moon phase would be more complex.
    // We can change the background color or add a simple image based on the phase
    let moonColor = "#CCCCCC"; // Default for full moon
    if (phase < 0.25) {
        moonColor = "#333333"; // New moon / waxing crescent
    } else if (phase < 0.5) {
        moonColor = "#666666"; // First quarter / waxing gibbous
    } else if (phase < 0.75) {
        moonColor = "#999999"; // Full moon / waning gibbous
    } else {
        moonColor = "#666666"; // Last quarter / waning crescent
    }
    moonPhaseDiv.style.backgroundColor = moonColor;

    // You could also add more complex SVG or image-based moon phases here
    // For example, by changing a background image or manipulating SVG circles
});
