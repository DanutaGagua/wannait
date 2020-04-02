# Architecture To be  

Application type: web  
Architecture type: client-server  
Reason of choice: all users need access to the same data from different devices  
Advantages: security, centralized access to data, easy maintenance  

![Architecture To be](https://github.com/L1ttl3S1st3r/wannait/blob/master/Documents/Design/ComponentsAndDeployment/components.jpg)

# Architecture As is  

![Architecture As is](https://github.com/L1ttl3S1st3r/wannait/blob/master/Documents/Design/ComponentsAndDeployment/components.jpg)
![Class diagram](https://github.com/L1ttl3S1st3r/wannait/blob/master/Documents/Design/ComponentsAndDeployment/components.jpg)

# Comparing

Both architectures don't have any differencies, because previous developer (our Product Owner) made application how it needs to be. We can do one thing: check and fix dependencies between backend servers and database.

# Improvement

We can add several frontend servers (not only one), each of them would work with several backend servers, to decrease overload on each frontend server. It would be useful if many consumers would use this application at the same time.
