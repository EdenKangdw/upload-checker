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
          DEFAULT: "#F3CA52",
          1: "#F6E9B2",
          // 2: "#ADBC9F",
          // 3: "#FBFADA",
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
    },
  },
};
