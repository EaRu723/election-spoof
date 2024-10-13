function remixHeadline(headline) {
    // A basic remixed version of the headline
    const funnyEndings = [
      "but with a tinfoil hat.",
      "while juggling flaming swords.",
      "and then aliens showed up.",
      "underwater, because why not?",
      "in the upside-down world."
    ];
  
    // Pick a random funny ending
    const randomEnding = funnyEndings[Math.floor(Math.random() * funnyEndings.length)];
    
    // Combine the headline with a twist
    return `${headline}... ${randomEnding}`;
  }
  
  export default remixHeadline;
  