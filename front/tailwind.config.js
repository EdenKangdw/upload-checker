/** @type {import('tailwindcss').Config} */
module.exports = {
  // content: [
  //   "./src/**/*.{js,jsx,ts,tsx}",
  //   // "./pages/**/*.{html,js}",
  //   // "./components/**/*.{html,js}",
  // ],
  content: [ 
    "./src/**/*.{js,jsx,ts,tsx}",
    "./node_modules/react-tailwindcss-datepicker/dist/index.esm.js",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#e9f5db",
          1:"#cfe1b9",
          2: "#b5c99a",
          3: "#97a97c",
          4: "#87986a",
          5: "#718355",
        },
        secondary: {
          DEFAULT: "#CCD5AE",
          1: "#E9EDC9",
          2: "#FEFAE0",
          3: "#FAEDCD",
        },
        button: {
          DEFAULT: "#ED9455",
          1: "#FFBB70",
          2: "#FFEC9E",
          3: "#FFFBDA",
        },
        text:{
          DEFAULT: "#27374D",
        }
      },
      spacing: {
        sm: "4px",
        md: "8px",
        lg: "12px",
      },
      screens: {
        sm: "640px",
        md: "768px",
      },
      content: {
        'plusIcon': 'url("../src/assets/images/icon/ico-plus.svg")',
      },
      fontFamily: {
        'ownglyph': ['Ownglyph_ryuttung-Rg', 'sans-serif'],
      },
    },
  },
};
