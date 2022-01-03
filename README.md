# YoloV4-predictive-object-search-robot

### Note: informal writing for non technical audiences
The following has been altered to improve readiblity for a non technical auidence.
If you are interested in a formal paper, please send me a request on this page.

## What is a predictive object search robot and why is it important?
Ever been on the sofa and felt too comfy to get a cold soda from the fridge? Ever dreamt about a robot that could get you anything and do chores around the house? Well, look no further than the predictive object search robot! Its here to make your life lazier! I mean easier!

#### Sounds good, what is it? 

This project presents a predictive object search robot, that can quickly find, never before seen objects in the home environment by prediciting their location. How you may ask? Well, it achieves this by using a model that exploits patterns seen in the home environment. Hasn’t someone done this before? Yes and no. Most object finding/retrieval robots require a structured environment to operate. This means that they must know the exact location of objects beforehand, and the objects must be placed in an easy-to-pick formation. Both these requirements are not practical in a home. if we were to use such current state-of-the-art machines to find/retrieve objects in the home, they would be unable to find/retrieve the object, in suitable time. 

#### Before I see/read your work, is your method even tested on real robots?

Yes, it has! This project is a recreation of the work done in the papers below. The system presented here was created independently, but the same idea was implemented. From both the papers the esteemed computer scientists showed that this system exceled compared to current state of the art solutions. These results were obtained by implementing the system on high end robots.

[1]	https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=8374184

[2]	https://link.springer.com/epdf/10.1007

## How does the robot work?
For the robot to find seen/unseen objects in the home, it needs two things. Firstly, the ability to identify objects at home. Secondly a model which allows the robot to interpret the information it has observed. Ok, so how did you resolve both of these requirements? For the robot to identify objects, the robot was equipped with a camera and the output of that was fed into YoloV3. YoloV3 is an object detection framework that uses a single neural network to identify objects in an image (see here). Then to create the second part, which is the model. The home environment was analysed and broken down into some patterns.
One such pattern, observed was, that as humans we tend to cluster objects of similar function together, for example, toys will be near other toys, cooking tools in the kitchen will be near other cooking tools, etc. this pattern can be used by the robot to find unseen objects. How….? Well, if the robot had seen a spoon and a bicycle, and I were to tell it to find me a fork. It would first search near the knife since it is more similar to a fork then a bicycle. So essentially, it will go to the kitchen rather than the garage to find a fork. That’s the basic idea. 

## Lets see if it works!
To test if the robot can find unseen objects, the robot will be placed in the centre of a room surrounded by four tables. Each table will contain similar functioning items. For example, we will have a food table, office table, garage/sport table and lastly an animal table. for the test we will instruct the robot to find a sports-ball. The outcome we want is the robot to approach the sports table first to search for the ball. Check the video, to see if we achieved this outcome!

(coming soon)
if you saw the video, you saw the robot first approached the sports table to search for the ball. Great we achieved the expected outcome! (more concrete scientific evidence can be found in the 2 papers mentioned above).

## An understanding of the steps the robot takes to find an unseen object (Brief).
This section doesn’t explain the steps taken by the robot with an example, this may make it difficult to understand. I suggest you watch the video above which will go through all the steps and then to read this brief and next detailed section.
When the robot is turned on it spins/roams in the room to notice as many objects in the room as it can. This step is important so that the robot can compare any object it is queried to find with objects it has seen. After that, the robot can take requests from users as to what object they would like the robot to find. We’ll call it the “query object”. 

The robot then does a semantic comparison using Word2Vec to find which items it has seen on the tables is most like the queried object. it will create a path to make the robot approach tables in the order of closest matching to least matching table. 

After that the robot will inspect the tables in the path. If it finds the object it will stop searching for it and return “object found”. If the object is not found on that table, it will continue to the next table until it finds it. if it doesn’t find the queried object on any of the tables, the robot will return “item not found on any tables”. Then it will return to waiting for the user to input an object for the robot to find.

## An understanding of the steps the robot takes to find an unseen object (Detailed).
This section gives a detailed overview of the steps the robot takes to find a queried object. if you haven’t done so already, please watch the video above before reading this section. It may help you in understanding it.
The UML state machine diagram below shows the states the robot enters to find an object.

![](uml_diagrams/robot%20state%20machine.png)

* * Figure is a UML state machine diagram that shows all the states of the robot

The robot consists of 6 states. These states have been described in the following UML activity diagram to see easily what methods are involved in each state. It has been created so it can be followed as the steps below are read.

![](uml_diagrams/robot%20uml%20diagram.png)
 
* * Figure shows a UML activity diagram which illustrates the functions involved in each state of the robot

The state machine starts in initial spinning state, in which the robot notices objects in the room. This step is important so that the robot can compare any object it is queried to find with objects it has seen. In this state, the robot spins on the spot, in the centre of the room. Where it uses YoloV3 on the camera input, to get detections of the objects in the scene. Since YoloV3 has a likelihood of getting false predictions, the detections are filtered. For each object the robot detects, it calculates the global coordinate of it, so that it can be approached by the robot later in the state machine. Also, the robot clusters the objects that are most similar in function together. since the objects on each of the tables are similar to each other. A cluster is made of those objects. After this process we get 4 clusters, an office items cluster, food, sports, and animal clusters. (Why cluster? See answer [1] in questions section below).

Once the robot has completed one rotation, the spinning state ends and the robot transitions to the awaiting commands state. In this state, the user is prompted to input, on the keyboard, an object to find. Once the input has been received the robot transitions to the processing command state

In the processing command state the input is tokenised and normalised, so it conforms to Word2Vec format.  Then, it is processed with Word2Vec, to return a list of tables ordered by similarity to the queried object (why return a list of similar tables and not similar objects? See [2] in questions section below) . After that, the robot transitions to navigating to destination state

in this state the robot approaches the table. (that is it, if u read on, the rest of the paragraph explains the technicalities of how it approaches the table. it’s complicated) To approach the table the robot converts the global coordinate of the table to a coordinate of the table in the perspective of the robot using forward kinematics calculations. This step is important as the robot can only navigate to the table if the coordinate of the table is in the perspective of the robot. Once the coordinates is calculated, the robot approaches the table by rotating towards it and moving forward. Only to stop at defined region from the table. This is to ensure the robot doesn't go under the table and to give enough distance for the robot to observe the objects on the table. 

After approaching the table, the robot transitions to inspecting table state. In this state the robot spins left to right to inspect the objects on the table. This state gives the robot a chance to observe all the objects on the table more clearly, which it wasn't able to do in the initial spinning state. After that, the robot enters the verifying object state

In this state, it checks if the queried object is present on that table the robot approached. if the object is present, the user will be prompted with the message “object found!” and the robot will return to the awaiting command state to ask the user for another object to find. If the object is not found, the robot will navigate to the remaining tables in order of similarity to queried object, until the object is found. if the robot has checked all the tables and the object is still not found it will prompt the user with the message “sorry object not found on any table” and will return to the awaiting command state, to ask the user to look for another object. 
This concludes the detailed description of the steps the robot takes to find a seen/unseen object. If you have any questions please send me a message on GitHub 😊. 

#### Questions:
##### [1]	Why clustering objects? 
Well, it reduces the number of times a robot needs to approach an object to verify it. when the robot sees an object from afar, it will try to recognise it but it won’t be 100%, therefore the robot needs to approach the object to see the object clearly and ensure that the object actually exists. if we had a knife, spoon and a fork on a table next to each other. Without a cluster, the robot would have to go to each of the items individually to verify them. However, if they are clustered the robot can come to a location, where it can verify all the objects in the cluster.

##### [2]	In processing command state, why does the robot return a list of similar tables and not similar objects?
As said in [1], the tables represent a cluster of similar objects. So the robot only has to go to one location to observe all the objects in the table (cluster). If the robot were to approach and check every object individually it would take too long and become infeasible to use the robot.

## So, what are the plans for the future?
Well as you saw in the video or read the result, the robot does work well, and is able to find most the objects on its first attempt. However, for it to end up in your home, a lot of development needs to be done on all aspect of the robot so it can work safely at home with your family.
If you are interested in this project and would like to be updated on future work, please feel free to send me a response on this page. If there is a lot of interest I will try to publish and update the developments of the project on other platforms as well. Hopefully we can have a kick starter or Patreon set up, so we can have helping robots in our homes soon! 
If you have gotten this far, thanks so much for taking the time to read up on my project. I will continue working on domestic (home) robots to make the lives people everywhere better!

