You can find all the necessary packages in the "requirements.json"
-------------------------------------------------------

How to install missing packages (for example "numba" package):
1.open OSGeo4W Shell;
2.use the command: py3_env;
3.search the command to install packages using the package manager - pip (for example Google search: "pip numba");
4.use the command: pip install "packageName" (for example: pip install numba).

p.s. if you are having problems with pip, try the following steps, and then repeat the basic steps:
1. check pip version: pip --version;
2. if you get an error, you should install pip in QGIS Python;
3. open OSGeo4W Shell;
4. go to any non-system folder (for example to Desktop: (windows 10) cd C:/users/UserName/Desktop);
5. use the command: curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py;
6. use the command: python get-pip.py
7. close OSGeo4W Shell.


Why do we use third-party packages:
We use third-party packages to speed up some of our code that processes large amounts of data.
For example, Numba - "Numba translates Python functions to optimized machine code at runtime using the industry-standard LLVM compiler library. 
Numba-compiled numerical algorithms in Python can approach the speeds of C or FORTRAN.": https://numba.pydata.org/
We use OpenCV to work with images: https://opencv.org/
