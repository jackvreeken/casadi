#
#     This file is part of CasADi.
# 
#     CasADi -- A symbolic framework for dynamic optimization.
#     Copyright (C) 2010 by Joel Andersson, Moritz Diehl, K.U.Leuven. All rights reserved.
# 
#     CasADi is free software; you can redistribute it and/or
#     modify it under the terms of the GNU Lesser General Public
#     License as published by the Free Software Foundation; either
#     version 3 of the License, or (at your option) any later version.
# 
#     CasADi is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#     Lesser General Public License for more details.
# 
#     You should have received a copy of the GNU Lesser General Public
#     License along with CasADi; if not, write to the Free Software
#     Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
# 
# 
from casadi import *
import casadi as c
from numpy import *
import unittest
from types import *
from helpers import *
import itertools

#CasadiOptions.setCatchErrorsPython(False)

solvers= []
 
try:
  solvers.append((WorhpSolver,{}))
  print "Will test WorhpSolver"
except:
  pass
  
try:
  solvers.append((IpoptSolver,{}))
  print "Will test IpoptSolver"
except:
  pass

try:
  solvers.append((SnoptSolver,{"_verify_level": 3,"detect_linear": True,"_optimality_tolerance":1e-10,"_feasibility_tolerance":1e-10}))
  print "Will test SnoptSolver"
except:
  pass

try:
  qp_solver_options = {"nlp_solver": IpoptSolver, "nlp_solver_options": {"tol": 1e-12} }
  solvers.append((SQPMethod,{"qp_solver": NLPQPSolver,"qp_solver_options": qp_solver_options}))
  print "Will test SQPMethod"
except:
  pass
  
try:
  qp_solver_options = {"nlp_solver": IpoptSolver, "nlp_solver_options": {"tol": 1e-12, "print_level": 0, "print_time": False} }
  solvers.append((StabilizedSQPMethod,{"tol_pr": 1e-9, "tol_du": 1e-9,"stabilized_qp_solver": QPStabilizer, "stabilized_qp_solver_options": {"qp_solver": NLPQPSolver, "qp_solver_options": qp_solver_options}}))
  print "Will test SQPMethod"
except:
  pass

#try:
#  solvers.append(KnitroSolver)
#  print "Will test KnitroSolver"
#except:
#  pass
  
class NLPtests(casadiTestCase):

  def testboundsviol(self):
    x=SX.sym("x")
    nlp=SXFunction(nlpIn(x=x),nlpOut(f=(x-1)**2,g=x))
    
    for Solver, solver_options in solvers:
      solver = Solver(nlp)
      solver.setOption(solver_options)
      for k,v in ({"tol":1e-5,"hessian_approximation":"limited-memory","max_iter":100, "MaxIter": 100,"print_level":0,"derivative_test":"first-order" }).iteritems():
        if solver.hasOption(k):
          solver.setOption(k,v)
       
      solver.init()
      solver.setInput([-10],"lbx")
      solver.setInput([-20],"ubx")
      solver.setInput([-10],"lbg")
      solver.setInput([10],"ubg")
      with self.assertRaises(Exception):
        solver.solve()

    for Solver, solver_options in solvers:
      solver = Solver(nlp)
      solver.setOption(solver_options)
      for k,v in ({"tol":1e-5,"hessian_approximation":"limited-memory","max_iter":100, "MaxIter": 100,"print_level":0,"derivative_test":"first-order" }).iteritems():
        if solver.hasOption(k):
          solver.setOption(k,v)
       
      solver.init()
      solver.setInput([-10],"lbx")
      solver.setInput([10],"ubx")
      solver.setInput([-10],"lbg")
      solver.setInput([-20],"ubg")
      with self.assertRaises(Exception):
        solver.solve()
        
  def testIPOPT(self):
    x=SX.sym("x")
    nlp=SXFunction(nlpIn(x=x),nlpOut(f=(x-1)**2,g=x))
    
    for Solver, solver_options in solvers:
      self.message("trivial " + str(Solver))
      solver = Solver(nlp)
      solver.setOption(solver_options)
      for k,v in ({"tol":1e-5,"hessian_approximation":"limited-memory","max_iter":100, "MaxIter": 100,"print_level":0,"derivative_test":"first-order" }).iteritems():
        if solver.hasOption(k):
          solver.setOption(k,v)
       
      solver.init()
      solver.setInput([-10],"lbx")
      solver.setInput([10],"ubx")
      solver.setInput([-10],"lbg")
      solver.setInput([10],"ubg")
      solver.solve()
      self.assertAlmostEqual(solver.getOutput("f")[0],0,10,str(Solver))
      self.assertAlmostEqual(solver.getOutput("x")[0],1,9,str(Solver))
      self.assertAlmostEqual(solver.getOutput("g")[0],1,9,str(Solver))
      self.assertAlmostEqual(solver.getOutput("lam_x")[0],0,9,str(Solver))
      self.assertAlmostEqual(solver.getOutput("lam_g")[0],0,9,str(Solver))
      
  def testIPOPT_par(self):
    x=SX.sym("x")
    p=SX.sym("p")
    nlp=SXFunction(nlpIn(x=x,p=p),nlpOut(f=(x-p)**2,g=x))
    
    for Solver, solver_options in solvers:
      self.message("trivial " + str(Solver))
      solver = Solver(nlp)
      solver.setOption(solver_options)
      for k,v in ({"tol":1e-5,"hessian_approximation":"limited-memory","max_iter":100, "MaxIter": 100,"print_level":0,"derivative_test":"first-order"}).iteritems():
        if solver.hasOption(k):
          solver.setOption(k,v)
      solver.init()
      solver.setInput([-10],"lbx")
      solver.setInput([10],"ubx")
      solver.setInput([-10],"lbg")
      solver.setInput([10],"ubg")
      solver.setInput(1,"p")
      solver.solve()
      self.assertAlmostEqual(solver.getOutput("f")[0],0,10,str(Solver))
      self.assertAlmostEqual(solver.getOutput("x")[0],1,9,str(Solver))
      self.assertAlmostEqual(solver.getOutput("lam_x")[0],0,9,str(Solver))
      self.assertAlmostEqual(solver.getOutput("lam_g")[0],0,9,str(Solver))
      
  def testIPOPTinf(self):
    self.message("trivial IPOPT, infinity bounds")
    x=SX.sym("x")
    nlp=SXFunction(nlpIn(x=x),nlpOut(f=(x-1)**2,g=x))
    
    for Solver, solver_options in solvers:
      self.message(str(Solver))
      solver = Solver(nlp)
      solver.setOption(solver_options)
      for k,v in ({"tol":1e-5,"hessian_approximation":"limited-memory","max_iter":100, "MaxIter": 100,"print_level":0,"derivative_test":"first-order"}).iteritems():
        if solver.hasOption(k):
          solver.setOption(k,v)
      solver.init()
      solver.setInput([-Inf],"lbx")
      solver.setInput([Inf],"ubx")
      solver.setInput([-Inf],"lbg")
      solver.setInput([Inf],"ubg")

      if 'Worhp' in str(Solver):
        with self.assertRaises(Exception):
          solver.solve()
        return




      solver.solve()
      self.assertAlmostEqual(solver.getOutput("f")[0],0,10,str(Solver))
      self.assertAlmostEqual(solver.getOutput("x")[0],1,7,str(Solver) + str(solver.getOutput("x")[0]-1))
      self.assertAlmostEqual(solver.getOutput("lam_x")[0],0,9,str(Solver))
      self.assertAlmostEqual(solver.getOutput("lam_g")[0],0,9,str(Solver))
      
  def testIPOPTrb(self):
    self.message("rosenbrock, limited-memory hessian approx")
    x=SX.sym("x")
    y=SX.sym("y")
    
    nlp=SXFunction(nlpIn(x=vertcat([x,y])),nlpOut(f=(1-x)**2+100*(y-x**2)**2))
    
    for Solver, solver_options in solvers:
      self.message(str(Solver))
      solver = Solver(nlp)
      solver.setOption(solver_options)
      for k,v in ({"tol":1e-9,"TolOpti":1e-14,"hessian_approximation":"limited-memory","max_iter":100, "MaxIter": 100,"print_level":0,"derivative_test":"first-order"}).iteritems():
        if solver.hasOption(k):
          solver.setOption(k,v)
      solver.init()
      solver.setInput([-10]*2,"lbx")
      solver.setInput([10]*2,"ubx")
      solver.solve()
      self.assertAlmostEqual(solver.getOutput("f")[0],0,10,str(Solver))
      self.assertAlmostEqual(solver.getOutput("x")[0],1,6,str(Solver))
      self.assertAlmostEqual(solver.getOutput("x")[1],1,6,str(Solver))
      self.assertAlmostEqual(solver.getOutput("lam_x")[0],0,5,str(Solver))
      self.assertAlmostEqual(solver.getOutput("lam_x")[1],0,5,str(Solver))
    
  def testIPOPTrb2(self):
    self.message("rosenbrock, limited-memory hessian approx")
    x=SX.sym("x")
    y=SX.sym("y")
    
    nlp=SXFunction(nlpIn(x=vertcat([x,y])),nlpOut(f=(1-x)**2+100*(y-x**2)**2,g=x+y))
    for Solver, solver_options in solvers:
      self.message(str(Solver))
      solver = Solver(nlp)
      solver.setOption(solver_options)
      for k,v in ({"tol":1e-8,"TolOpti":1e-20,"hessian_approximation":"limited-memory","max_iter":1000, "MaxIter": 100,"print_level":0,"derivative_test":"first-order"}).iteritems():
        if solver.hasOption(k):
          solver.setOption(k,v)
      solver.init()
      solver.setInput([-10]*2,"lbx")
      solver.setInput([10]*2,"ubx")
      solver.setInput([-10],"lbg")
      solver.setInput([10],"ubg")
      solver.solve()
      
      digits = 6

      self.assertAlmostEqual(solver.getOutput("f")[0],0,digits,str(Solver))
      self.assertAlmostEqual(solver.getOutput("x")[0],1,digits,str(Solver))
      self.assertAlmostEqual(solver.getOutput("x")[1],1,digits,str(Solver))
      self.assertAlmostEqual(solver.getOutput("lam_x")[0],0,5,str(Solver))
      self.assertAlmostEqual(solver.getOutput("lam_x")[1],0,5,str(Solver))
      self.assertAlmostEqual(solver.getOutput("lam_g")[0],0,5,str(Solver))
      
  def testIPOPTrbf(self):
    self.message("rosenbrock fixed, limited-memory hessian approx")
    x=SX.sym("x")
    y=SX.sym("y")
    
    nlp=SXFunction(nlpIn(x=vertcat([x,y])),nlpOut(f=(1-x)**2+100*(y-x**2)**2,g=x+y))
    for Solver, solver_options in solvers:
      self.message(str(Solver))
      solver = Solver(nlp)
      solver.setOption(solver_options)
      for k,v in ({"tol":1e-8,"TolOpti":1e-20,"hessian_approximation":"limited-memory","max_iter":100, "MaxIter": 100,"print_level":0,"derivative_test":"first-order"}).iteritems():
        if solver.hasOption(k):
          solver.setOption(k,v)
      solver.init()
      solver.setInput([0,1],"x0")
      solver.setInput([-10,1],"lbx")
      solver.setInput([10,1],"ubx")
      solver.setInput([-10],"lbg")
      solver.setInput([10],"ubg")

      if 'Worhp' in str(Solver):
        with self.assertRaises(Exception):
          solver.solve()
        return




      solver.solve()
      self.assertAlmostEqual(solver.getOutput("f")[0],0,10,str(Solver))
      self.assertAlmostEqual(solver.getOutput("x")[0],1,7,str(Solver))
      self.assertAlmostEqual(solver.getOutput("x")[1],1,7,str(Solver))
      if "Stabilized" not in str(Solver):
        self.assertAlmostEqual(solver.getOutput("lam_x")[0],0,6,str(Solver))
        self.assertAlmostEqual(solver.getOutput("lam_x")[1],0,6,str(Solver))
        self.assertAlmostEqual(solver.getOutput("lam_g")[0],0,6,str(Solver))
      
  def testIPOPTrhb2(self):
    self.message("rosenbrock, exact hessian, constrained")
    x=SX.sym("x")
    y=SX.sym("y")
    
    obj = (1-x)**2+100*(y-x**2)**2
    nlp=SXFunction(nlpIn(x=vertcat([x,y])),nlpOut(f=obj,g=x**2+y**2))
    
    c_r = 4.56748075136258e-02;
    x_r = [7.86415156987791e-01,6.17698316967954e-01]
    
    sigma=SX.sym("sigma")
    lambd=SX.sym("lambd")
    h=SXFunction(hessLagIn(x=vertcat([x,y]),lam_f=sigma,lam_g=lambd),
                 hessLagOut(hess=sigma*hessian(obj,vertcat([x,y]))+lambd*hessian(nlp.outputExpr("g"),vertcat([x,y]))))
    h.init()
    h.setInput([0.5,0.5])
    h.setInput(-40,1)
    h.setInput(1,2)
    h.evaluate()
    print h.getOutput()
    
    solver = None
    for Solver, solver_options in solvers:
      self.message(str(Solver))
      solver = Solver(nlp)
      solver.setOption(solver_options)
      solver.setOption("hess_lag",h)
      for k,v in ({"tol":1e-10,"TolOpti":1e-20,"hessian_approximation":"exact","UserHM":True,"max_iter":100, "MaxIter": 100,"derivative_test":"second-order"}).iteritems():
        if solver.hasOption(k):
          solver.setOption(k,v)
          
      solver.init()
      solver.setInput([0.5,0.5],"x0")
      solver.setInput([-10]*2,"lbx")
      solver.setInput([10]*2,"ubx")
      solver.setInput([0],"lbg")
      solver.setInput([1],"ubg")
      solver.solve()
      
      digits = 5
        
      self.assertAlmostEqual(solver.getOutput("f")[0],c_r,digits,str(Solver))
      self.assertAlmostEqual(solver.getOutput("x")[0],x_r[0],digits,str(Solver))
      self.assertAlmostEqual(solver.getOutput("x")[1],x_r[1],digits,str(Solver))
      self.assertAlmostEqual(solver.getOutput("lam_x")[0],0,8,str(Solver))
      self.assertAlmostEqual(solver.getOutput("lam_x")[1],0,8,str(Solver))
      self.assertAlmostEqual(solver.getOutput("lam_g")[0],0.12149655447670,6,str(Solver))
      
  def test_warmstart(self):
  
    x=SX.sym("x")
    y=SX.sym("y")
    
    obj = (1-x)**2+100*(y-x**2)**2
    nlp=SXFunction(nlpIn(x=vertcat([x,y])),nlpOut(f=obj,g=x**2+y**2))
    
    c_r = 4.56748075136258e-02;
    x_r = [7.86415156987791e-01,6.17698316967954e-01]
    
    for Solver, solver_options in solvers:
      self.message(str(Solver))
      solver = Solver(nlp)
      solver.setOption(solver_options)
      for k,v in ({"tol":1e-10,"TolOpti":1e-20,"hessian_approximation":"exact","UserHM":True,"max_iter":100, "MaxIter": 100,"derivative_test":"second-order"}).iteritems():
        if solver.hasOption(k):
          solver.setOption(k,v)
      solver.init()
      solver.setInput([0.5,0.5],"x0")
      solver.setInput([-10]*2,"lbx")
      solver.setInput([10]*2,"ubx")
      solver.setInput([0],"lbg")
      solver.setInput([1],"ubg")
      solver.solve()
      
      digits = 5
        
      self.assertAlmostEqual(solver.getOutput("f")[0],c_r,digits,str(Solver))
      self.assertAlmostEqual(solver.getOutput("x")[0],x_r[0],digits,str(Solver))
      self.assertAlmostEqual(solver.getOutput("x")[1],x_r[1],digits,str(Solver))
      self.assertAlmostEqual(solver.getOutput("lam_x")[0],0,8,str(Solver))
      self.assertAlmostEqual(solver.getOutput("lam_x")[1],0,8,str(Solver))
      self.assertAlmostEqual(solver.getOutput("lam_g")[0],0.12149655447670,6,str(Solver))

      self.message(":warmstart")
      if "Ipopt" in str(Solver):
        oldsolver=solver
        solver = Solver(nlp)
        solver.setOption(solver_options)
        solver.setOption("warm_start_init_point","yes")
        solver.setOption("warm_start_bound_push",1e-6)
        solver.setOption("warm_start_slack_bound_push",1e-6)
        solver.setOption("warm_start_mult_bound_push",1e-6)
        solver.setOption("mu_init",1e-6)
        solver.init()
        solver.setInput([-10]*2,"lbx")
        solver.setInput([10]*2,"ubx")
        solver.setInput([0],"lbg")
        solver.setInput([1],"ubg")
        solver.setInput(oldsolver.getOutput("x"),"x0")
        solver.setInput(oldsolver.getOutput("lam_g"),"lam_g0")
        solver.setOutput(oldsolver.getOutput("lam_x"),"lam_x")
        
        
        solver.solve()

  def testIPOPTrhb2_gen(self):
    self.message("rosenbrock, exact hessian generated, constrained")
    x=SX.sym("x")
    y=SX.sym("y")
    
    obj = (1-x)**2+100*(y-x**2)**2
    nlp=SXFunction(nlpIn(x=vertcat([x,y])),nlpOut(f=obj,g=x**2+y**2))
    
    c_r = 4.56748075136258e-02;
    x_r = [7.86415156987791e-01,6.17698316967954e-01]
    
    sigma=SX.sym("sigma")
    lambd=SX.sym("lambd")
  
    for Solver, solver_options in solvers:
      self.message(str(Solver))
      solver = Solver(nlp)
      solver.setOption(solver_options)
      for k,v in ({"tol":1e-12,"TolOpti":1e-20,"hessian_approximation":"exact","UserHM":True,"max_iter":200, "MaxIter": 100,"print_level":1,"derivative_test":"second-order", "toldx": 1e-15, "tolgl": 1e-15}).iteritems():
        if solver.hasOption(k):
          solver.setOption(k,v)
          
      solver.init()
      solver.setInput([0.5,0.5],"x0")
      solver.setInput([-10]*2,"lbx")
      solver.setInput([10]*2,"ubx")
      solver.setInput([0],"lbg")
      solver.setInput([1],"ubg")
      solver.solve()
      
      digits = 5
      
      self.assertAlmostEqual(solver.getOutput("f")[0],c_r,digits,str(Solver) + str(solver.getOutput("f")[0]) + ":" + str(c_r))
      self.assertAlmostEqual(solver.getOutput("x")[0],x_r[0],digits,str(Solver))
      self.assertAlmostEqual(solver.getOutput("x")[1],x_r[1],digits,str(Solver))
      self.assertAlmostEqual(solver.getOutput("lam_x")[0],0,8,str(Solver))
      self.assertAlmostEqual(solver.getOutput("lam_x")[1],0,8,str(Solver))
      self.assertAlmostEqual(solver.getOutput("lam_g")[0],0.12149655447670,6,str(Solver))
      
      
  def test_jacG_empty(self):
    x=SX.sym("x")
    y=SX.sym("y")
    
    obj = (1-x)**2+100*(y-x**2)**2
    nlp=SXFunction(nlpIn(x=vertcat([x,y])),nlpOut(f=obj,g=1))
    
    for Solver, solver_options in solvers:
      self.message(str(Solver))
      if "Worhp" in str(Solver):
        continue
      solver = Solver(nlp)
      solver.setOption(solver_options)
      solver.init()
      solver.setInput([0.5,0.5],"x0")
      solver.setInput([-10]*2,"lbx")
      solver.setInput([10]*2,"ubx")
      solver.setInput([0],"lbg")
      solver.setInput([2],"ubg")
      solver.solve()
      
      digits = 5
        
      self.checkarray(solver.getOutput("f"),DMatrix([0]),str(Solver),digits=digits)
      self.checkarray(solver.getOutput("x"),DMatrix([1,1]),str(Solver),digits=digits)
      self.checkarray(solver.getOutput("lam_x"),DMatrix([0,0]),str(Solver),digits=digits)
      self.checkarray(solver.getOutput("lam_g"),DMatrix([0]),str(Solver),digits=digits)

  def testIPOPTrhb2_par(self):
    self.message("rosenbrock, exact hessian, constrained, ")
    x=SX.sym("x")
    y=SX.sym("y")
    p=SX.sym("p")
    
    obj = (p-x)**2+100*(y-x**2)**2
    nlp=SXFunction(nlpIn(x=vertcat([x,y]),p=p),nlpOut(f=obj,g=x**2+y**2))
    
    c_r = 4.56748075136258e-02;
    x_r = [7.86415156987791e-01,6.17698316967954e-01]
    
    sigma=SX.sym("sigma")
    lambd=SX.sym("lambd")
    h=SXFunction(hessLagIn(x=vertcat([x,y]),lam_f=sigma,lam_g=lambd,p=p),
                 hessLagOut(hess=sigma*hessian(obj,vertcat([x,y]))+lambd*hessian(nlp.outputExpr("g"),vertcat([x,y]))))

    for Solver, solver_options in solvers:
      self.message(str(Solver))
      solver = Solver(nlp)
      solver.setOption(solver_options)
      solver.setOption("hess_lag",h)
      for k,v in ({"tol":1e-10,"TolOpti":1e-20,"hessian_approximation":"exact","UserHM":True,"max_iter":100, "MaxIter": 100,"print_level":1,"derivative_test":"second-order"}).iteritems():
        if solver.hasOption(k):
          solver.setOption(k,v)
      solver.init()
      solver.setInput([0.5,0.5],"x0")
      solver.setInput([-10]*2,"lbx")
      solver.setInput([10]*2,"ubx")
      solver.setInput([0],"lbg")
      solver.setInput([1],"ubg")
      solver.setInput([1],"p")
      solver.solve()
      
      digits = 5
        
      self.assertAlmostEqual(solver.getOutput("f")[0],c_r,digits,str(Solver))
      self.assertAlmostEqual(solver.getOutput("x")[0],x_r[0],digits,str(Solver))
      self.assertAlmostEqual(solver.getOutput("x")[1],x_r[1],digits,str(Solver))
      self.assertAlmostEqual(solver.getOutput("lam_x")[0],0,8,str(Solver))
      self.assertAlmostEqual(solver.getOutput("lam_x")[1],0,8,str(Solver))
      self.assertAlmostEqual(solver.getOutput("lam_g")[0],0.12149655447670,6,str(Solver))

  def testIPOPTrhb2_gen_par(self):
    self.message("rosenbrock, exact hessian generated, constrained, parametric")
    x=SX.sym("x")
    y=SX.sym("y")
    p=SX.sym("p")
    
    obj = (p-x)**2+100*(y-x**2)**2
    nlp=SXFunction(nlpIn(x=vertcat([x,y]),p=p),nlpOut(f=obj,g=x**2+y**2))
    
    c_r = 4.56748075136258e-02;
    x_r = [7.86415156987791e-01,6.17698316967954e-01]
    
    sigma=SX.sym("sigma")
    lambd=SX.sym("lambd")
  
    for Solver, solver_options in solvers:
      self.message(str(Solver))
      solver = Solver(nlp)
      solver.setOption(solver_options)
      for k,v in ({"tol":1e-10,"TolOpti":1e-20,"hessian_approximation":"exact","UserHM":True,"max_iter":100, "MaxIter": 100,"print_level":1,"derivative_test":"second-order"}).iteritems():
        if solver.hasOption(k):
          solver.setOption(k,v)
          
      solver.init()
      solver.setInput([0.5,0.5],"x0")
      solver.setInput([-10]*2,"lbx")
      solver.setInput([10]*2,"ubx")
      solver.setInput([0],"lbg")
      solver.setInput([1],"ubg")
      solver.setInput([1],"p")
      solver.solve()
      
      digits = 5

      self.assertAlmostEqual(solver.getOutput("f")[0],c_r,digits,str(Solver))
      self.assertAlmostEqual(solver.getOutput("x")[0],x_r[0],digits,str(Solver))
      self.assertAlmostEqual(solver.getOutput("x")[1],x_r[1],digits,str(Solver))
      self.assertAlmostEqual(solver.getOutput("lam_x")[0],0,8,str(Solver))
      self.assertAlmostEqual(solver.getOutput("lam_x")[1],0,8,str(Solver))
      self.assertAlmostEqual(solver.getOutput("lam_g")[0],0.12149655447670,6,str(Solver))
      
  def testIPOPTrhb(self):
    self.message("rosenbrock, exact hessian")
    x=SX.sym("x")
    y=SX.sym("y")
    
    obj=(1-x)**2+100*(y-x**2)**2
    nlp=SXFunction(nlpIn(x=vertcat([x,y])),nlpOut(f=obj))
    
    sigma=SX.sym("sigma")
    
    h=SXFunction(hessLagIn(x=vertcat([x,y]),lam_f=sigma),
                 hessLagOut(hess=sigma*hessian(obj,vertcat([x,y]))))
    for Solver, solver_options in solvers:
      self.message(str(Solver))
      solver = Solver(nlp)
      solver.setOption(solver_options)
      solver.setOption("hess_lag",h)
      for k,v in ({"tol":1e-10,"TolOpti":1e-20,"hessian_approximation":"exact","UserHM":True,"max_iter":100, "MaxIter": 100,"print_level":0,"derivative_test":"first-order"}).iteritems():
        if solver.hasOption(k):
          solver.setOption(k,v)
      #solver.setOption("verbose",True)
      solver.init()
      solver.setInput([-10]*2,"lbx")
      solver.setInput([10]*2,"ubx")
      solver.solve()
      self.assertAlmostEqual(solver.getOutput("f")[0],0,10,str(Solver))
      self.assertAlmostEqual(solver.getOutput("x")[0],1,9,str(Solver))
      self.assertAlmostEqual(solver.getOutput("x")[1],1,9,str(Solver))
      self.assertAlmostEqual(solver.getOutput("lam_x")[0],0,8,str(Solver))
      self.assertAlmostEqual(solver.getOutput("lam_x")[1],0,8,str(Solver))

  def testIPOPTrhb_gen(self):
    self.message("rosenbrock, exact hessian generated")
    x=SX.sym("x")
    y=SX.sym("y")
    
    obj=(1-x)**2+100*(y-x**2)**2
    nlp=SXFunction(nlpIn(x=vertcat([x,y])),nlpOut(f=obj))
    
    sigma=SX.sym("sigma")
    
    for Solver, solver_options in solvers:
      self.message(str(Solver))
      solver = Solver(nlp)
      solver.setOption(solver_options)
      for k,v in ({"tol":1e-10,"TolOpti":1e-20,"hessian_approximation":"exact","UserHM":True,"max_iter":100, "MaxIter": 100,"print_level":0,"derivative_test":"first-order"}).iteritems():
        if solver.hasOption(k):
          solver.setOption(k,v)
      #solver.setOption("verbose",True)
      solver.init()
      solver.setInput([-10]*2,"lbx")
      solver.setInput([10]*2,"ubx")
      solver.solve()
      self.assertAlmostEqual(solver.getOutput("f")[0],0,10,str(Solver))
      self.assertAlmostEqual(solver.getOutput("x")[0],1,9,str(Solver))
      self.assertAlmostEqual(solver.getOutput("x")[1],1,9,str(Solver))
      self.assertAlmostEqual(solver.getOutput("lam_x")[0],0,8,str(Solver))
      self.assertAlmostEqual(solver.getOutput("lam_x")[1],0,8,str(Solver))

  def testIPOPTrhb_gen_xnonfree(self):
    self.message("rosenbrock, exact hessian generated, non-free x")
    x=SX.sym("x")
    y=SX.sym("y")
    
    obj=(1-x)**2+100*(y-x**2)**2
    nlp=SXFunction(nlpIn(x=vertcat([x,y])),nlpOut(f=obj))
    
    sigma=SX.sym("sigma")
    
    for Solver, solver_options in solvers:
      self.message(str(Solver))
      solver = Solver(nlp)
      solver.setOption(solver_options)
      for k,v in ({"tol":1e-10,"TolOpti":1e-20,"hessian_approximation":"exact","UserHM":True,"max_iter":100, "MaxIter": 100,"print_level":0,"derivative_test":"first-order"}).iteritems():
        if solver.hasOption(k):
          solver.setOption(k,v)
      #solver.setOption("verbose",True)
      solver.init()
      solver.setInput([1,-10],"lbx")
      solver.setInput([1,10],"ubx")

      if 'Worhp' in str(Solver):
        with self.assertRaises(Exception):
          solver.solve()
        return



      solver.solve()
      self.assertAlmostEqual(solver.getOutput("f")[0],0,10,str(Solver))
      self.assertAlmostEqual(solver.getOutput("x")[0],1,9,str(Solver))
      self.assertAlmostEqual(solver.getOutput("x")[1],1,6,str(Solver))
      self.assertAlmostEqual(solver.getOutput("lam_x")[0],0,6,str(Solver))
      self.assertAlmostEqual(solver.getOutput("lam_x")[1],0,6,str(Solver))
      
  def testIPOPTrhb_par(self):
    self.message("rosenbrock, exact hessian, parametric")
    x=SX.sym("x")
    y=SX.sym("y")
    
    p=SX.sym("p")
    obj=(p-x)**2+100*(y-x**2)**2
    nlp=SXFunction(nlpIn(x=vertcat([x,y]),p=p),nlpOut(f=obj))
    
    sigma=SX.sym("sigma")
    
    h=SXFunction(hessLagIn(x=vertcat([x,y]),p=p,lam_f=sigma),
                 hessLagOut(hess=sigma*hessian(obj,vertcat([x,y]))))
    for Solver, solver_options in solvers:
      self.message(str(Solver))
      solver = Solver(nlp)
      solver.setOption(solver_options)
      solver.setOption("hess_lag",h)
      for k,v in ({"tol":1e-10,"TolOpti":1e-20,"hessian_approximation":"exact","UserHM":True,"max_iter":100, "MaxIter": 100,"print_level":0,"derivative_test":"first-order"}).iteritems():
        if solver.hasOption(k):
          solver.setOption(k,v)
      #solver.setOption("verbose",True)
      solver.init()
      solver.setInput([-10]*2,"lbx")
      solver.setInput([10]*2,"ubx")
      solver.setInput(1,"p")
      solver.solve()
      self.assertAlmostEqual(solver.getOutput("f")[0],0,10,str(Solver))
      self.assertAlmostEqual(solver.getOutput("x")[0],1,9,str(Solver))
      self.assertAlmostEqual(solver.getOutput("x")[1],1,9,str(Solver))
      self.assertAlmostEqual(solver.getOutput("lam_x")[0],0,8,str(Solver))
      self.assertAlmostEqual(solver.getOutput("lam_x")[1],0,8,str(Solver))

  def testIPOPTrhb_gen_par(self):
    self.message("rosenbrock, exact hessian generated, parametric")
    x=SX.sym("x")
    y=SX.sym("y")
    
    p=SX.sym("p")
    obj=(p-x)**2+100*(y-x**2)**2
    nlp=SXFunction(nlpIn(x=vertcat([x,y]),p=p),nlpOut(f=obj))
    
    sigma=SX.sym("sigma")
    
    for Solver, solver_options in solvers:
      self.message(str(Solver))
      solver = Solver(nlp)
      solver.setOption(solver_options)
      for k,v in ({"tol":1e-10,"TolOpti":1e-20,"hessian_approximation":"exact","UserHM":True,"max_iter":100, "MaxIter": 100,"print_level":0,"derivative_test":"first-order"}).iteritems():
        if solver.hasOption(k):
          solver.setOption(k,v)
      #solver.setOption("verbose",True)
      solver.init()
      solver.setInput([-10]*2,"lbx")
      solver.setInput([10]*2,"ubx")
      solver.setInput(1,"p")
      solver.solve()
      self.assertAlmostEqual(solver.getOutput("f")[0],0,10,str(Solver))
      self.assertAlmostEqual(solver.getOutput("x")[0],1,9,str(Solver))
      self.assertAlmostEqual(solver.getOutput("x")[1],1,9,str(Solver))
      
  def testIPOPTnorm(self):
    self.message("IPOPT min ||x||^2_2")
    def norm_2(mx):
      return inner_prod(mx,mx)
    N=10
    x=MX.sym("x",N)
    x0=linspace(0,1,N)
    X0=MX(x0)
    nlp=MXFunction(nlpIn(x=x),nlpOut(f=norm_2(x-X0),g=2*x))
    for Solver, solver_options in solvers:
      self.message(str(Solver))
      solver = Solver(nlp)
      solver.setOption(solver_options)
      for k,v in ({"tol":1e-8,"max_iter":103, "MaxIter": 103,"print_level":0,"derivative_test":"first-order"}).iteritems():
        if solver.hasOption(k):
          solver.setOption(k,v)
      solver.init()
      solver.setInput([-10]*N,"lbx")
      solver.setInput([10]*N,"ubx")
      solver.setInput([-10]*N,"lbg")
      solver.setInput([10]*N,"ubg")
      solver.solve()
      print "residuals"
      print array(solver.getOutput("x")).squeeze()-x0
      print "bazmeg", solver.getOutput("f")
      self.assertAlmostEqual(solver.getOutput("f")[0],0,10,str(Solver))
      self.checkarray(array(solver.getOutput("x")).squeeze(),x0,str(Solver),digits=8)
      self.checkarray(solver.getOutput("lam_x"),DMatrix([0]*10),8,str(Solver),digits=8)
      self.assertAlmostEqual(solver.getOutput("lam_g")[1],0,8,str(Solver))
      
  def testIPOPTnoc(self):
    self.message("trivial IPOPT, no constraints")
    """ There is an assertion error thrown, but still it works"""
    x=SX.sym("x")
    nlp=SXFunction(nlpIn(x=x),nlpOut(f=(x-1)**2))
    for Solver, solver_options in solvers:
      self.message(str(Solver))
      solver = Solver(nlp)
      solver.setOption(solver_options)
      for k,v in ({"tol":1e-10,"max_iter":103, "MaxIter": 103,"print_level":0,"derivative_test":"first-order"}).iteritems():
        if solver.hasOption(k):
          solver.setOption(k,v)
      solver = IpoptSolver(nlp)
      solver.init()
      solver.setInput([-10],"lbx")
      solver.setInput([10],"ubx")
      solver.solve()
      self.assertAlmostEqual(solver.getOutput("f")[0],0,10,str(Solver))
      self.assertAlmostEqual(solver.getOutput("x")[0],1,9,str(Solver))
    
  def testIPOPTmx(self):
    self.message("trivial IPOPT, using MX")
    x=MX.sym("x")
    nlp=MXFunction(nlpIn(x=x),nlpOut(f=(x-1)**2,g=2*x))
    
    for Solver, solver_options in solvers:
      self.message(str(Solver))
      solver = Solver(nlp)
      solver.setOption(solver_options)
      for k,v in ({"tol":1e-10,"max_iter":103, "MaxIter": 103,"print_level":0,"derivative_test":"first-order"}).iteritems():
        if solver.hasOption(k):
          solver.setOption(k,v)
      solver.init()
      solver.setInput([-10],"lbx")
      solver.setInput([10],"ubx")
      solver.setInput([-10],"lbg")
      solver.setInput([10],"ubg")
      solver.solve()
      self.assertAlmostEqual(solver.getOutput("f")[0],0,10,str(Solver))
      self.assertAlmostEqual(solver.getOutput("x")[0],1,9,str(Solver))
    
  def testIPOPTc(self):
    self.message("trivial, overconstrained")
    x=SX.sym("x")
    nlp=SXFunction(nlpIn(x=x),nlpOut(f=(x-1)**2,g=vertcat([x,x,x])))
    
    for Solver, solver_options in solvers:
      self.message(str(Solver))
      solver = Solver(nlp)
      solver.setOption(solver_options)
      for k,v in ({"tol":1e-5,"max_iter":100, "MaxIter": 100,"print_level":0,"derivative_test":"first-order"}).iteritems():
        if solver.hasOption(k):
          solver.setOption(k,v)
      solver.init()
      solver.setInput([-10],"lbx")
      solver.setInput([10],"ubx")
      solver.setInput([-10, -10, -10],"lbg")
      solver.setInput([10, 10, 10],"ubg")
      solver.solve()
      self.assertAlmostEqual(solver.getOutput("f")[0],0,9,str(Solver) )
      self.assertAlmostEqual(solver.getOutput("x")[0],1,5,str(Solver))
    
  def testIPOPTc2(self):
    self.message("trivial2, overconstrained")
    x=SX.sym("x")
    nlp=SXFunction(nlpIn(x=x),nlpOut(f=(x-1)**2,g=vertcat([x,x,x+x])))
    
    for Solver, solver_options in solvers:
      self.message(str(Solver))
      solver = Solver(nlp)
      solver.setOption(solver_options)
      for k,v in ({"tol":1e-10,"max_iter":100, "hessian_approximation": "limited-memory", "MaxIter": 100,"print_level":0,"derivative_test":"first-order"}).iteritems():
        if solver.hasOption(k):
          solver.setOption(k,v)
      solver.init()
      solver.setInput([-10],"lbx")
      solver.setInput([10],"ubx")
      solver.setInput([-10, -10, -10],"lbg")
      solver.setInput([10, 10, 10],"ubg")
      solver.solve()
      self.assertAlmostEqual(solver.getOutput("f")[0],0,10,str(Solver))
      self.assertAlmostEqual(solver.getOutput("x")[0],1,8,str(Solver))
    
  def testIPOPTcmx(self):
    self.message("trivial , overconstrained, using MX")
    x=MX.sym("x")
    nlp=MXFunction(nlpIn(x=x),nlpOut(f=(x-1)**2,g=vertcat([2*x,3*x,4*x])))
    
    for Solver, solver_options in solvers:
      self.message(str(Solver))
      solver = Solver(nlp)
      solver.setOption(solver_options)
      for k,v in ({"tol":1e-10,"max_iter":100, "hessian_approximation": "limited-memory", "MaxIter": 100,"print_level":0,"derivative_test":"first-order"}).iteritems():
        if solver.hasOption(k):
          solver.setOption(k,v)
      solver.init()
      solver.setInput([-10],"lbx")
      solver.setInput([10],"ubx")
      solver.setInput([-10,-10,-10],"lbg")
      solver.setInput([10,10,10],"ubg")
      solver.solve()
      self.assertAlmostEqual(solver.getOutput("f")[0],0,9,str(Solver))
      self.assertAlmostEqual(solver.getOutput("x")[0],1,8,str(Solver))

  def testIPOPTdeg(self):
    self.message("degenerate optimization IPOPT")
    x=SX.sym("x")
    y=SX.sym("y")
    nlp=SXFunction(nlpIn(x=vertcat([x,y])),nlpOut(f=0,g=vertcat([x-y,x])))
    for Solver, solver_options in solvers:
      self.message(str(Solver))
      solver = Solver(nlp)
      solver.setOption(solver_options)
      for k,v in ({"tol":1e-5,"max_iter":100, "hessian_approximation": "limited-memory", "MaxIter": 100,"print_level":0,"derivative_test":"first-order"}).iteritems():
        if solver.hasOption(k):
          solver.setOption(k,v)
      solver.init()
      solver.setInput([-10, -10],"lbx")
      solver.setInput([10, 10],"ubx")
      solver.setInput([0, 3],"lbg")
      solver.setInput([0, 3],"ubg")
      solver.solve()
      self.assertAlmostEqual(solver.getOutput("x")[0],solver.getOutput("x")[1],10,"IPOPT")

  def testIPOPTdegc(self):
    self.message("degenerate optimization IPOPT, overconstrained")
    x=SX.sym("x")
    y=SX.sym("y")
    nlp=SXFunction(nlpIn(x=vertcat([x,y])),nlpOut(f=0,g=vertcat([x-y,x,x+y])))
    
    for Solver, solver_options in solvers:
      self.message(str(Solver))
      solver = Solver(nlp)
      solver.setOption(solver_options)
      for k,v in ({"tol":1e-5,"max_iter":100, "hessian_approximation": "limited-memory", "MaxIter": 100,"print_level":0,"derivative_test":"first-order"}).iteritems():
        if solver.hasOption(k):
          solver.setOption(k,v)

      solver.init()
      solver.setInput([-10, -10],"lbx")
      solver.setInput([10, 10],"ubx")
      solver.setInput([0, 3 , -10],"lbg")
      solver.setInput([0, 3, 10],"ubg")
      solver.solve()
      # todo: catch error when set([0, 3 , 5]) two times
      self.assertAlmostEqual(solver.getOutput("x")[0],solver.getOutput("x")[1],10,"IPOPT")
      
  def testXfreeChange(self):
    self.message("Change in X settings")
    x=SX.sym("x")
    y=SX.sym("y")
    
    nlp=SXFunction(nlpIn(x=vertcat([x,y])),nlpOut(f=(1-x)**2+100*(y-x**2)**2,g=x+y))
    for Solver, solver_options in solvers:
      self.message(str(Solver))
      solver = Solver(nlp)
      solver.setOption(solver_options)
      for k,v in ({"tol":1e-8,"TolOpti":1e-20,"hessian_approximation":"limited-memory","max_iter":100, "MaxIter": 100,"print_level":0,"derivative_test":"first-order"}).iteritems():
        if solver.hasOption(k):
          solver.setOption(k,v)
      solver.init()
      solver.setInput([0,1],"x0")
      solver.setInput([-10,-10],"lbx")
      solver.setInput([10,10],"ubx")
      solver.setInput([-10],"lbg")
      solver.setInput([10],"ubg")
      solver.solve()
      solver.setInput([-10,1],"lbx")
      solver.setInput([10,1],"ubx")
      solver.setInput([-10],"lbg")
      solver.setInput([10],"ubg")

      if 'Worhp' in str(Solver):
        with self.assertRaises(Exception):
          solver.solve()
        return


      solver.solve()
      
      self.assertAlmostEqual(solver.getOutput("f")[0],0,10,str(Solver))
      self.assertAlmostEqual(solver.getOutput("x")[0],1,7,str(Solver))
      self.assertAlmostEqual(solver.getOutput("x")[1],1,7,str(Solver))

  def testactiveLBX(self):
    self.message("active LBX")
    x=SX.sym("x")
    y=SX.sym("y")
    
    nlp=SXFunction(nlpIn(x=vertcat([x,y])),nlpOut(f=(1-x)**2+100*(y-x**2)**2,g=x+y))
    for Solver, solver_options in solvers:
      self.message(str(Solver))
      solver = Solver(nlp)
      solver.setOption(solver_options)
      for k,v in ({"tol":1e-8,"TolOpti":1e-20,"max_iter":100, "MaxIter": 100,"print_level":0,"derivative_test":"first-order", "hessian_approximation": "exact", "UserHM": True}).iteritems():
        if solver.hasOption(k):
          solver.setOption(k,v)
      solver.init()
      solver.setInput([0,1],"x0")
      solver.setInput([-10,1.2],"lbx")
      solver.setInput([10,2],"ubx")
      solver.setInput([-10],"lbg")
      solver.setInput([10],"ubg")
      solver.solve()
      self.assertAlmostEqual(solver.getOutput("f")[0],9.0908263002590e-3,6,str(Solver))
      self.assertAlmostEqual(solver.getOutput("x")[0],1.0952466252248,6,str(Solver))
      self.assertAlmostEqual(solver.getOutput("x")[1],1.2,5,str(Solver))
      self.assertAlmostEqual(solver.getOutput("lam_x")[0],0,8,str(Solver))
      self.assertAlmostEqual(solver.getOutput("lam_x")[1],-8.6963632695079e-2,4,str(Solver))
      self.assertAlmostEqual(solver.getOutput("lam_g")[0],0,8,str(Solver))

  def testactiveLBG(self):
    self.message("active LBG")
    x=SX.sym("x")
    y=SX.sym("y")
    
    nlp=SXFunction(nlpIn(x=vertcat([x,y])),nlpOut(f=(1-x)**2+100*(y-x**2)**2,g=x+y))
    for Solver, solver_options in solvers:
      self.message(str(Solver))
      solver = Solver(nlp)
      solver.setOption(solver_options)
      for k,v in ({"tol":1e-8,"TolOpti":1e-20,"max_iter":100, "MaxIter": 100,"print_level":0,"derivative_test":"first-order", "hessian_approximation": "exact", "UserHM": True }).iteritems():
        if solver.hasOption(k):
          solver.setOption(k,v)
      solver.init()
      solver.setInput([0,1],"x0")
      solver.setInput([-10,-10],"lbx")
      solver.setInput([10,10],"ubx")
      solver.setInput([2.2],"lbg")
      solver.setInput([10],"ubg")
      solver.solve()
      self.assertAlmostEqual(solver.getOutput("f")[0],4.252906468284e-3,6,str(Solver))
      self.assertAlmostEqual(solver.getOutput("x")[0],1.065181061847138,6,str(Solver))
      self.assertAlmostEqual(solver.getOutput("x")[1],1.1348189166291160,6,str(Solver))
      self.assertAlmostEqual(solver.getOutput("lam_x")[0],0,8,str(Solver))
      self.assertAlmostEqual(solver.getOutput("lam_x")[1],0,4,str(Solver))
      self.assertAlmostEqual(solver.getOutput("lam_g")[0],-4.1644422845712e-2,3,str(Solver))

  def testactiveUBG(self):
    self.message("active UBG")
    x=SX.sym("x")
    y=SX.sym("y")
    
    nlp=SXFunction(nlpIn(x=vertcat([x,y])),nlpOut(f=(1-x)**2+100*(y-x**2)**2,g=x+y))
    for Solver, solver_options in solvers:
      self.message(str(Solver))
      solver = Solver(nlp)
      solver.setOption(solver_options)
      for k,v in ({"tol":1e-8,"TolOpti":1e-20,"max_iter":100, "MaxIter": 100,"print_level":0,"derivative_test":"first-order", "hessian_approximation": "exact", "UserHM": True}).iteritems():
        if solver.hasOption(k):
          solver.setOption(k,v)
      solver.init()
      solver.setInput([0,1],"x0")
      solver.setInput([-10,-10],"lbx")
      solver.setInput([10,10],"ubx")
      solver.setInput([0],"lbg")
      solver.setInput([1.8],"ubg")
      solver.solve()
      self.assertAlmostEqual(solver.getOutput("f")[0],4.64801220074552e-3,6,str(Solver))
      self.assertAlmostEqual(solver.getOutput("x")[0],9.318651964592811e-1,5,str(Solver))
      self.assertAlmostEqual(solver.getOutput("x")[1],8.68134821123689e-1,5,str(Solver))
      self.assertAlmostEqual(solver.getOutput("lam_x")[0],0,8,str(Solver))
      self.assertAlmostEqual(solver.getOutput("lam_x")[1],0,4,str(Solver))
      self.assertAlmostEqual(solver.getOutput("lam_g")[0],4.75846495145007e-2,5,str(Solver))
      
  def testactiveUBX(self):
    self.message("active UBX")
    x=SX.sym("x")
    y=SX.sym("y")
    
    nlp=SXFunction(nlpIn(x=vertcat([x,y])),nlpOut(f=(1-x)**2+100*(y-x**2)**2,g=x+y))
    for Solver, solver_options in solvers:
      self.message(str(Solver))
      solver = Solver(nlp)
      solver.setOption(solver_options)
      for k,v in ({"tol":1e-8,"TolOpti":1e-20,"max_iter":100, "MaxIter": 100,"print_level":0,"derivative_test":"first-order", "hessian_approximation": "exact", "UserHM": True}).iteritems():
        if solver.hasOption(k):
          solver.setOption(k,v)
      solver.init()
      solver.setInput([0,1],"x0")
      solver.setInput([-10,0],"lbx")
      solver.setInput([10,0.9],"ubx")
      solver.setInput([-10],"lbg")
      solver.setInput([10],"ubg")
      solver.solve()
      self.assertAlmostEqual(solver.getOutput("f")[0],2.626109721583e-3,6,str(Solver))
      self.assertAlmostEqual(solver.getOutput("x")[0],9.4882542279172277e-01,6,str(Solver))
      self.assertAlmostEqual(solver.getOutput("x")[1],0.9,6,str(Solver))
      self.assertAlmostEqual(solver.getOutput("lam_x")[0],0,8,str(Solver))
      self.assertAlmostEqual(solver.getOutput("lam_x")[1],5.39346608659e-2,4,str(Solver))
      self.assertAlmostEqual(solver.getOutput("lam_g")[0],0,8,str(Solver))
      
  def test_QP(self):
    self.message("QP")

    N = 50 

    x = SX.sym("x",N)
    x0 = DMatrix(range(N))
    H = diag(range(1,N+1))
    obj = 0.5*mul([(x-x0).T,H,(x-x0)])

    nlp = SXFunction(nlpIn(x=x),nlpOut(f=obj))
    for Solver, solver_options in solvers:
      self.message(str(Solver))
      solver = Solver(nlp)
      solver.setOption(solver_options)
      for k,v in ({"tol":1e-8,"tol_pr":1e-10,"TolOpti":1e-25,"hessian_approximation":"limited-memory","max_iter":100, "MaxIter": 100,"print_level":0}).iteritems():
        if solver.hasOption(k):
          solver.setOption(k,v)
      solver.init()
      solver.setInput(-1000,"lbx")
      solver.setInput(1000,"ubx")
      solver.solve()
      self.checkarray(solver.getOutput("x"),x0,str(Solver),digits=2)
      self.assertAlmostEqual(solver.getOutput("f")[0],0,3,str(Solver))
      self.checkarray(solver.getOutput("lam_x"),DMatrix.zeros(N,1),str(Solver),digits=4)
      
      
  def test_tol_pr(self):
    return
    self.message("Low tol_pr")
    H = DMatrix([[1,-1],[-1,2]])
    G = DMatrix([-2,-6])
    A =  DMatrix([[1, 1],[-1, 2],[2, 1]])

    LBA = DMatrix([-inf]*3)
    UBA = DMatrix([2, 2, 3])

    LBX = DMatrix([0.5,0])
    UBX = DMatrix([0.5,inf])

    x=SX.sym("x",2)
    nlp=SXFunction(nlpIn(x=x),nlpOut(f=0.5*mul([x.T,H,x])+mul(G.T,x),g=mul(A,x)))

    for Solver, solver_options in solvers:
      self.message(str(Solver))
      solver = Solver(nlp)
      solver.setOption(solver_options)
      for k,v in ({"tol":1e-8,"tol_pr":1e-10,"TolOpti":1e-25,"hessian_approximation":"limited-memory","max_iter":100,"MaxIter": 100,"print_level":0, "fixed_variable_treatment": "make_constraint"}).iteritems():
        if solver.hasOption(k):
          solver.setOption(k,v)
          
      solver.init()
      solver.setInput(LBX,"lbx")
      solver.setInput(UBX,"ubx")
      solver.setInput(LBA,"lbg")
      solver.setInput(UBA,"ubg")

      solver.solve()

      self.assertAlmostEqual(solver.getOutput()[0],0.5,6,str(Solver))
      self.assertAlmostEqual(solver.getOutput()[1],1.25,6,str(Solver))
    
      self.assertAlmostEqual(solver.getOutput("lam_x")[0],4.75,6,str(Solver))
      self.assertAlmostEqual(solver.getOutput("lam_x")[1],0,6,str(Solver))

      self.checkarray(solver.getOutput("lam_g"),DMatrix([0,2,0]),str(Solver),digits=6)
      
      self.assertAlmostEqual(solver.getOutput("f")[0],-7.4375,6,str(Solver))
      
  def test_QP2(self):
    H = DMatrix([[1,-1],[-1,2]])
    G = DMatrix([-2,-6])
    A =  DMatrix([[1, 1],[-1, 2],[2, 1]])

    LBA = DMatrix([-inf]*3)
    UBA = DMatrix([2, 2, 3])

    LBX = DMatrix([0.5,0])
    UBX = DMatrix([0.5,inf])

    x=SX.sym("x",2)
    nlp=SXFunction(nlpIn(x=x),nlpOut(f=0.5*mul([x.T,H,x])+mul(G.T,x),g=mul(A,x)))

    for Solver, solver_options in solvers:
      self.message(str(Solver))
      solver = Solver(nlp)
      solver.setOption(solver_options)
      for k,v in ({"tol":1e-8,"TolOpti":1e-25,"hessian_approximation":"limited-memory","max_iter":100,"MaxIter": 100,"print_level":0, "fixed_variable_treatment": "make_constraint"}).iteritems():
        if solver.hasOption(k):
          solver.setOption(k,v)
          
      solver.init()
      solver.setInput(LBX,"lbx")
      solver.setInput(UBX,"ubx")
      solver.setInput(LBA,"lbg")
      solver.setInput(UBA,"ubg")
      if 'Worhp' in str(Solver):
        with self.assertRaises(Exception):
          solver.solve()
        return

      solver.solve()

      self.assertAlmostEqual(solver.getOutput()[0],0.5,6,str(Solver))
      self.assertAlmostEqual(solver.getOutput()[1],1.25,6,str(Solver))
    
      self.assertAlmostEqual(solver.getOutput("lam_x")[0],4.75,6,str(Solver))
      self.assertAlmostEqual(solver.getOutput("lam_x")[1],0,6,str(Solver))

      self.checkarray(solver.getOutput("lam_g"),DMatrix([0,2,0]),str(Solver),digits=6)
      
      self.assertAlmostEqual(solver.getOutput("f")[0],-7.4375,6,str(Solver))
      
      solver = Solver(nlp)
      solver.setOption(solver_options)
      for k,v in ({"tol":1e-8,"TolOpti":1e-25,"hessian_approximation":"exact","UserHM":True,"max_iter":100,"MaxIter": 100,"print_level":0, "fixed_variable_treatment": "make_constraint"}).iteritems():
        if solver.hasOption(k):
          solver.setOption(k,v)
          
      solver.init()
      solver.setInput(LBX,"lbx")
      solver.setInput(UBX,"ubx")
      solver.setInput(LBA,"lbg")
      solver.setInput(UBA,"ubg")

      solver.solve()

      self.assertAlmostEqual(solver.getOutput()[0],0.5,6,str(Solver))
      self.assertAlmostEqual(solver.getOutput()[1],1.25,6,str(Solver))
    
      self.assertAlmostEqual(solver.getOutput("lam_x")[0],4.75,6,str(Solver))
      self.assertAlmostEqual(solver.getOutput("lam_x")[1],0,6,str(Solver))

      self.checkarray(solver.getOutput("lam_g"),DMatrix([0,2,0]),str(Solver),digits=6)
      
      self.assertAlmostEqual(solver.getOutput("f")[0],-7.4375,6,str(Solver))

  def test_QP2_unconvex(self):
    H = DMatrix([[1,-1],[-1,-2]])
    G = DMatrix([-2,-6])
    A =  DMatrix([[1, 1],[-1, 2],[2, 1]])
    
    LBA = DMatrix([-inf]*3)
    UBA = DMatrix([2, 2, 3])

    LBX = DMatrix([0]*2)
    UBX = DMatrix([inf]*2)

    x=SX.sym("x",2)
    nlp=SXFunction(nlpIn(x=x),nlpOut(f=0.5*mul([x.T,H,x])+mul(G.T,x),g=mul(A,x)))

    for Solver, solver_options in solvers:
      self.message(str(Solver))
      solver = Solver(nlp)
      solver.setOption(solver_options)
      for k,v in ({"tol":1e-8,"TolOpti":1e-25,"hessian_approximation":"limited-memory","max_iter":100,"MaxIter": 100,"print_level":0, "fixed_variable_treatment": "make_constraint"}).iteritems():
        if solver.hasOption(k):
          solver.setOption(k,v)
          
      solver.init()
      solver.setInput(LBX,"lbx")
      solver.setInput(UBX,"ubx")
      solver.setInput(LBA,"lbg")
      solver.setInput(UBA,"ubg")

      solver.solve()

      self.assertAlmostEqual(solver.getOutput()[0],2.0/3,6,str(solver))
      self.assertAlmostEqual(solver.getOutput()[1],4.0/3,6,str(solver))
    
      self.assertAlmostEqual(solver.getOutput("lam_x")[0],0,6,str(solver))
      self.assertAlmostEqual(solver.getOutput("lam_x")[1],0,6,str(solver))

      self.checkarray(solver.getOutput("lam_g"),DMatrix([4+8.0/9,20.0/9,0]),str(solver),digits=6)
      
      self.assertAlmostEqual(solver.getOutput("f")[0],-10-16.0/9,6,str(solver))

      solver = Solver(nlp)
      solver.setOption(solver_options)
      for k,v in ({"tol":1e-8,"TolOpti":1e-25,"hessian_approximation":"exact","UserHM":True,"max_iter":100,"MaxIter": 100,"print_level":0, "fixed_variable_treatment": "make_constraint"}).iteritems():
        if solver.hasOption(k):
          solver.setOption(k,v)
          
      solver.init()
      solver.setInput(LBX,"lbx")
      solver.setInput(UBX,"ubx")
      solver.setInput(LBA,"lbg")
      solver.setInput(UBA,"ubg")

      solver.solve()

      self.assertAlmostEqual(solver.getOutput()[0],2.0/3,6,str(solver))
      self.assertAlmostEqual(solver.getOutput()[1],4.0/3,6,str(solver))
    
      self.assertAlmostEqual(solver.getOutput("lam_x")[0],0,6,str(solver))
      self.assertAlmostEqual(solver.getOutput("lam_x")[1],0,6,str(solver))

      self.checkarray(solver.getOutput("lam_g"),DMatrix([4+8.0/9,20.0/9,0]),str(solver),digits=6)
      
      self.assertAlmostEqual(solver.getOutput("f")[0],-10-16.0/9,6,str(solver))
      
  def test_bug(self):
    x = MX.sym("x", 3)
    y = MX.sym("y", 2)
    f = MXFunction([x, y], [1.])
    f.init()
    aa = MX.sym("aa", 5)
    a = aa[:3]
    b = aa[3:]
    [f_call] = f.call([a, b])
    nlp = MXFunction(nlpIn(x=aa), nlpOut(f=f_call))
    for Solver, solver_options in solvers:
      solver = Solver(nlp)
      solver = IpoptSolver(nlp)
      solver.init() 
      
  @requires("SnoptSolver")
  def test_permute(self):
    for permute_g in itertools.permutations(range(3)):
      for permute_x in itertools.permutations(range(4)):
        x=SX.sym("x",4)
        x1,x2,x3,x4 = x[permute_x]
        g = [x1**2+x2**2+x3,
            x2**4+x4,
            2*x1+4*x2]
        f= (x1+x2+x3)**2+3*x3+5*x4
        F= SXFunction(nlpIn(x=x),nlpOut(f=f,g=vertcat(g)[permute_g]))
        F.init()
        
        solver = SnoptSolver(F)
        solver.init()

        solver.input("ubx")[permute_x]= DMatrix([inf,inf,inf,inf])
        solver.input("lbx")[permute_x]= DMatrix([-inf,-inf,0,0])
        
        solver.setInput(DMatrix([2,4,inf])[permute_g],"ubg")
        solver.setInput(DMatrix([2,4,0])[permute_g],"lbg")
        
        solver.input("x0")[permute_x] = DMatrix([-0.070,1.41,0,0.0199])
        solver.evaluate()


        F.setInput(solver.output("x"))
        F.evaluate()

        self.checkarray(solver.output("f"),DMatrix([1.900124999054007]))
        self.checkarray(solver.output("x")[permute_x],DMatrix([-7.0622015054877127e-02,1.4124491251009053e+00,0,1.9925001159906402e-02]))
        self.checkarray(solver.output("lam_x")[permute_x],DMatrix([0,0,-2.4683779217362773e+01,0]),digits=7)
        self.checkarray(solver.output("lam_g"),DMatrix([1.9000124997270717e+01,-5,0])[permute_g])
        #self.checkarray(solver.output("g"),DMatrix([2,4,5.50855])[permute_g])
  
  @requires("SnoptSolver")
  def test_classifications(self):      
    x=SX.sym("x")
    y=SX.sym("y")
    nlp=SXFunction(nlpIn(x=vertcat([x,y])),nlpOut(f=(1-x)**2+7.7*y,g=y**2))

    solver = SnoptSolver(nlp)
    solver.init()
        
    #solver.setOption("detect_linear",False)
    solver.setOption("verbose",True)
    solver.setOption("monitor",["setup_nlp","eval_nlp"])
    solver.setOption("_verify_level",3)
    #solver.setOption("_optimality_tolerance",1e-8)
    #solver.setOption("_feasibility_tolerance",1e-8)
    solver.setOption("_iteration_limit",1000)

    sparsegradF = nlp.jacobian("x","f")
    sparsegradF.init()
    ins = nlp.symbolicInput()
    out = list(sparsegradF.call(ins))
    sparsegradF = MXFunction(ins,[out[0].T] + out[1:])
    sparsegradF.init()

    solver.setOption("grad_f",sparsegradF)

    solver.init()
    solver.setInput([1,1],"x0")
    solver.setInput([-10,0],"lbx")
    solver.setInput([10,2],"ubx")
    solver.setInput([-10],"lbg")
    solver.setInput([10],"ubg")

    solver.solve()
    
    self.checkarray(solver.output("f"),DMatrix([0]))
    self.checkarray(solver.output("x"),DMatrix([1,0]))
    self.checkarray(solver.output("lam_x"),DMatrix([0,-7.7]),digits=7)
    self.checkarray(solver.output("lam_g"),DMatrix([0]))
    
if __name__ == '__main__':
    unittest.main()
    print solvers

