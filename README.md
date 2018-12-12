# Concept Mining from Course Material

This project is about concept mining from course material. The goal of this project is to extract concepts from the lecture slide (Microsoft PowerPoint), determine the relations among those concepts and how important those concepts are, and finally come up with UI that students can use. The student can use it to enhance their learning experience and review the course material. The prototype can be accessed on https://theconcepts.updog.co/home.html.

powerpoint.py

This file is used to parse a lecture slide (MS Power Point) and maintain structures that will be used for further process.

concepts.py

This file is used to extract concepts from a parsed lecture slide.

build_graph.py

This file is used to build a graph from extracted concepts and perfrom grpah analytics.
