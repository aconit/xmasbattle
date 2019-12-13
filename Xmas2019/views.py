"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template
from flask import Flask, session
from Xmas2019 import app
from qiskit import QuantumCircuit, execute, Aer, IBMQ
from flask import request

import os
import random
import math
import operator



@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html'
    )

@app.route('/gameindex')
def gameindex():
    """Renders the home page."""
    return render_template(
        'gameindex.html'
    )

@app.route('/playround/')
def playround():
     roundnumber= request.args.get('round', default = 1, type = int)
    
     if roundnumber == 6:
         qlausscore= session['qlausscore']
         yourscore = session['yourscore'] 
         return render_template(
             'gameover.html',
             yourscore  = yourscore,
             qlausscore  = qlausscore 
         )


     secamount = 5
     giftamount = 4
     maxweight = 5000

     if roundnumber==2:
         secamount = 6
         maxweight = 6000
         giftamount = 6
     elif roundnumber == 3:
         secamount =7 
         maxweight = 7000
         giftamount = 8
     elif roundnumber == 4:
         secamount = 8
         maxweight = 8000
         giftamount = 10
     elif roundnumber == 5:
         secamount = 9
         maxweight = 9000
         giftamount = 12

     if roundnumber == 1:
         session['qlausscore']=0
         session['yourscore'] =0

     session['round']=roundnumber 
     session['secamount']=secamount
     session['maxweight']=maxweight
     session['giftamount']=giftamount

     return render_template(
        'playround.html',
        roundnumber  = roundnumber,
        secamount  = secamount,
        maxweight=maxweight,
        giftamount = giftamount
    )

@app.route('/play/')
def play():
     giftamount= session['giftamount']
     maxweight = session['maxweight']
     secamount  = session['secamount']
     gifts = []

     avWeight = int(maxweight/giftamount)
     ampWeight = int(avWeight/4)
     ampLow = avWeight - ampWeight
     ampHigh  = avWeight + ampWeight

     for x in range(giftamount):
        temp = random.randint(ampLow, ampHigh)
        gifts.append(str(temp))

     session['gifts'] = gifts

     giftsstring = "|".join(gifts)
     
     return render_template(
        'play.html',
         gifts=giftsstring,
         giftamount = giftamount,
         secamount = secamount,
         maxweight=maxweight
    )


@app.route('/qlaus/')
def qlaus():
    yourresult= request.args.get('yourresult', default = 0, type = int)
    session['yourresult'] = yourresult
    
    giftamount =session['giftamount']
    gifts=session['gifts']
    maxweight = session['maxweight']

    # Use Aer's qasm_simulator
    simulator = Aer.get_backend('qasm_simulator')

    # Create a Quantum Circuit acting on the q register
    circuit = QuantumCircuit(giftamount+1,  giftamount +1)

    # Add a H gate to the first giftamount qubits
    for i in range(giftamount):
        circuit.h(i)

    #translate giftweights into angles
    angles=[]
    for i in range(giftamount):
        angles.append(math.pi * int(gifts[i])/maxweight)

    #add the rotations to the last qubit
    lastqubitnumber = giftamount-1
    for i in range(giftamount):
        circuit.cu3(angles[0], 0, 0, i, giftamount)

    qubits = []
    for i in range(giftamount+1):
        qubits.append(i)
    
    # Map the quantum measurement to the classical bits
    circuit.measure(qubits, qubits)

    # Execute the circuit on the qasm simulator
    job = execute(circuit, simulator, shots=2048)

    # Grab results from the job
    result = job.result()

    # Returns counts
    counts = result.get_counts(circuit)

    #get the results with the last qubit equal to 1
    filledcounts=counts.copy()

    for x in counts:
        if x[0]!='1':
            filledcounts.pop(x)
 

    # get the result with the highest probability
    qlauschoice=max(filledcounts.items(), key=operator.itemgetter(1))[0]
    
    session['qlauschoice'] =qlauschoice

    giftsstring = "|".join(gifts)

    return render_template(
        'qlaus.html',
        giftsstring=giftsstring,
        maxweight=maxweight,
        qlauschoice= qlauschoice
    )


@app.route('/endround/')
def endround():
    qlausresult= request.args.get('qlausresult', default = 0, type = int)
    yourresult = session['yourresult']
    maxweight = session['maxweight']
    qlausscore = session['qlausscore']
    yourscore=session['yourscore']
    roundnumber = session['round']

    if qlausresult > maxweight and yourresult<=maxweight:
        yourscore+=1
    elif yourresult>maxweight and qlausresult<=maxweight:
        qlausscore+=1
    elif qlausresult<=maxweight and yourresult<=maxweight:
        if qlausresult>yourresult:
            qlausscore+=1
        elif yourresult > qlausresult:
            yourscore+=1

    session['qlausscore'] = qlausscore
    session['yourscore'] = yourscore

    return render_template(
        'endround.html',
        qlausresult = qlausresult,
        yourresult=yourresult,
        qlausscore=qlausscore,
        yourscore=yourscore,
        maxweight=maxweight,
        roundnumber = roundnumber

    )


@app.route('/howtoplay/')
def howtoplay():
    
     return render_template(
        'howtoplay.html'
    )

