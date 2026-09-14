/**
 * This is a minimal config.
 *
 * If you need the full config, get it from here:
 * https://unpkg.com/browse/tailwindcss@latest/stubs/defaultConfig.stub.js
 */

module.exports = {
  content: [
    /**
     * HTML. Paths to Django template files that will contain Tailwind CSS classes.
     */

    /*  Templates within theme app (<tailwind_app_name>/templates), e.g. base.html. */
    "../templates/**/*.html",

    /*
     * Main templates directory of the project (BASE_DIR/templates).
     * Adjust the following line to match your project structure.
     */
    "../../templates/**/*.html",

    /*
     * Templates in other django apps (BASE_DIR/<any_app_name>/templates).
     * Adjust the following line to match your project structure.
     */
    "../../**/templates/**/*.html",

    /**
     * JS: If you use Tailwind CSS in JavaScript, uncomment the following lines and make sure
     * patterns match your project structure.
     */
    /* JS 1: Ignore any JavaScript in node_modules folder. */
    // '!../../**/node_modules',
    /* JS 2: Process all JavaScript files in the project. */
    // '../../**/*.js',

    /**
     * Python: If you use Tailwind CSS classes in Python, uncomment the following line
     * and make sure the pattern below matches your project structure.
     */
    // '../../**/*.py'
  ],
  theme: {
    extend: {
      colors: {
        cwg: {
          ink: "#272A2B",
          "ink-light": "#414647",
          "ink-dark": "#191C1D",
          paper: "#FCF9F1",
          "paper-dark": "#F1EBDD",
          brick: "#8F3F35",
          "brick-light": "#B76559",
          "brick-dark": "#6F2F29",
          brass: "#7A5626",
          "brass-light": "#C49A5A",
          "brass-dark": "#5D401B",
          sage: "#596653",
          "sage-light": "#8A9680",
          "sage-dark": "#414C3D",
          union: "#435A6B",
          confederate: "#8F3F35",

          // Compatibility aliases while older templates move to semantic names.
          red: "#8F3F35",
          "red-light": "#B76559",
          "red-dark": "#6F2F29",
          blue: "#7A5626",
          "blue-light": "#C49A5A",
          "blue-dark": "#5D401B",
          black: "#272A2B",
          "black-light": "#414647",
          "black-dark": "#191C1D",
          white: "#FCF9F1",
          green: "#596653",
          "green-light": "#8A9680",
          "green-dark": "#414C3D",
        },
      },
      fontFamily: {
        serif: ['Charter', 'Bitstream Charter', 'Sitka Text', 'Cambria', 'serif'],
      },
    },
  },
  plugins: [
    /**
     * '@tailwindcss/forms' is the forms plugin that provides a minimal styling
     * for forms. If you don't like it or have own styling for forms,
     * comment the line below to disable '@tailwindcss/forms'.
     */
    require("@tailwindcss/forms"),
    require("@tailwindcss/typography"),
  ],
};
