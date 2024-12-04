# ScottyBrowser

## Project Overview  
**Scottybrowser** is a unique web browsing application designed with a focus on usability and innovation. Unlike traditional browsers where tabs are displayed horizontally, this project features a vertical tab layout, maximizing screen space for content while offering a sleek, organized user experience.  

Built using **CMU Graphics**.

---

## Features  
- **Vertical Tab Layout**:  
  - Tabs are displayed along the side of the browser, offering more vertical space for web pages.  
  - Simplifies navigation when managing multiple tabs.

- **Interactive User Interface**:  
  - Dynamic tab creation and closing.
  - search bar built from complete scratch

- **Custom CMU-Inspired vibes**:  
  - A color scheme based on CMU's palette to give the browser a unique visual identity.  
  - I also included multiple odes and mentions of Scotty, CMU's mascot.

- **Performance Optimizations**:  
  - We render the sites using clever techniques and interact solely through RAM, avoiding any frame loss and drops

---

## Installation  
1. Clone this repository to your local machine and navigate to the directory.

2. Ensure you have Python installed, along with the **CMU Graphics** library. You also need a working version of **PIL**, which should be installed alongside CMU Graphics. You can install it using:  
   ```bash  
   pip install cmu-graphics
   ```  
3. Ensure that you have **Selenium** installed.
```bash
   pip install selenium
   ```  
4.  Ensure that you have a valid and working chromeDriver installed. Usually it's enough to just have chrome installed, but in certain senarios, you need to install a chrome driver and specifcy the path inside of backend/driver.py. In that case, navigate to the python code block in the following link should solve any problems.

  
  https://developer.chrome.com/docs/chromedriver/get-started
5. Run the project from the root directory:  
   ```bash  
   python -m draw.draw
   ```  
We run it in -m for module mode, if this doesnt work, please make sure you have a working version of python as well 
---

## How It Works  
1. **Rendering Engine**: Parses HTML and CSS to render simple static web pages.  
2. **Vertical Tab Management**:  
   - Add new tabs with a button click.  
   - Close tabs with a right-click.  
   - Switch between tabs with a single click.  
3. **Event Handling**: Interactive components and smooth user interaction powered by CMU Graphics.  

---

## Acknowledgments  
This project is a component of the F24 iteration of the 15-112 Fundamentals of Programming and Computer Science course at Carnegie Mellon University. Special thanks to **Dr. Ryan Riley** and the course staff, particularly **Mohamed Shikfa** for their guidance and support throughout the semester!

---  

## Contact  
**Author**: Adam Abu Ghaida, adamghaida.com 
Feel free to reach out!