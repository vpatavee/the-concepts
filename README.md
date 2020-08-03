# Concept Mining from Course Material

This project is about concept mining from course material. The goal of this project is to extract concepts from the lecture slide (Microsoft PowerPoint), determine the relations among those concepts and how important those concepts are, and finally come up with UI that students can use. The student can use it to enhance their learning experience and review the course material. For more info, see [full report](https://drive.google.com/file/d/1SCOWVFXG7RVE5w-NuPqLX6kT-kWU3PmS/view?usp=sharing).
 

The project can be separated in two the following steps.

1. Concepts extraction - This part I use NLP techniques to extract the concept from lecture
slides. This [file](powerpoint.py) is used to parse a lecture slide (MS Power Point) and maintain structures that will be used for further process.
This [file](concepts.py) is used to extract concepts from a parsed lecture slide.

2. Graph Analytics - After I extract the concepts, I determine the relations among those
concepts and how important those concepts using Page Rank. This [file](build_graph.py) is used to build a graph from extracted concepts and perfrom grpah analytics.

3. User Interface - I store all these data obtained from part 1 and part 2 in Firebase
Realtime Database that can be accessed and modified easily via UI. I write the website
that student can access and use this prototype. The HTML demonstrating the prototype of this work is in the [folder](web)
