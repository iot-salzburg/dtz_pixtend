// Salzburg Research ForschungsgesmbH
// Armin Niedermueller

// OPC UA Server on PiXtend

#include <iostream>
#include <fstream>
#include <algorithm>
#include <time.h>
#include <string>

#include <thread>
#include <chrono>

#include <opc/ua/node.h>
#include <opc/ua/subscription.h>
#include <opc/ua/server/server.h>



using namespace OpcUa;

class SubClient : public SubscriptionHandler
{
  void DataChange(uint32_t handle, const Node & node, const Variant & val, AttributeId attr) override
  {
    std::cout << "Received DataChange event for Node " << node << std::endl;
  }
};

std::vector<OpcUa::Variant> MyMethod(NodeId context, std::vector<OpcUa::Variant> arguments)
{
  std::cout << "MyMethod called! " << std::endl;
  std::vector<OpcUa::Variant> result;
  result.push_back(Variant(static_cast<uint8_t>(0)));
  return result;
}

void RunServer()
{
  // First setup our server
  auto logger = spdlog::stderr_color_mt("server");
  OpcUa::UaServer server(logger);
  server.SetEndpoint("opc.tcp://localhost:4840/freeopcua/server");
  server.SetServerURI("urn://exampleserver.freeopcua.github.io");
  server.Start();

  // then register our server namespace and get its index in server
  uint32_t idx = server.RegisterNamespace("Namespace - DTZ PiXtend");

  // Create our address space using different methods
  Node objects = server.GetObjectsNode();

  // Add a Node named "Parameters" with the id "1" and in namespace idx (index)
  NodeId nid(1, idx);
  QualifiedName qn("Parameters", idx);
  Node param_object = objects.AddObject(nid, qn);  
    
  // Add a variable and a property with auto-generated nodeid to our custom object
  Node conbelt_state = param_object.AddVariable(idx, "Conveyorbelt - State", Variant(8));
  Node conbelt_distance = param_object.AddVariable(idx, "Conveyorbelt - Distance", Variant(8.8));
  Node conbelt_drive = param_object.AddMethod(idx, "Conveyorbelt - Drive Control", MyMethod);


  // browse root node on server side
  Node root = server.GetRootNode();
  logger->info("Root node is: {}", root);
  logger->info("Children are:");

  for (Node node : root.GetChildren())
    {
      logger->info("    {}", node);
    }


  // Uncomment following to subscribe to datachange events inside server
  /*
  SubClient clt;
  std::unique_ptr<Subscription> sub = server.CreateSubscription(100, clt);
  sub->SubscribeDataChange(conbelt_state);
  */



  // Now write values to address space and send events so clients can have some fun
  conbelt_state.SetValue(Variant("init")); //will change value and trigger datachange event
  conbelt_distance.SetValue(Variant(0.0)); 

  // Create event
  server.EnableEventNotification();
  Event ev(ObjectId::BaseEventType); // you should create your own type
  ev.Severity = 2;
  ev.SourceNode = ObjectId::Server;
  ev.SourceName = "Event from FreeOpcUA";
  ev.Time = DateTime::Current();

  // define filestreams
  std::ifstream statefile("state.log");
  std::ifstream distancefile ("distance.log");
  std::string line;

  logger->info("Ctrl-C to exit");

  for (;;)
    {

	  // read conbelt_state from file and set value inside our object
	  getline(statefile, line);
      conbelt_state.SetValue(Variant(line));		// will change value and trigger datachange event


	  // read conbelt_distance from file and set value inside our object
	  getline(distancefile, line);
	  std::string::size_type sz;			 
	  double distance = std::stod(line, &sz);	
	  conbelt_distance.SetValue(Variant(distance)); // will change value and trigger datachange event


      std::stringstream ss;
	  ss << "This is an conbelt_state change event";
      ev.Message = LocalizedText(ss.str());
      server.TriggerEvent(ev);
      std::this_thread::sleep_for(std::chrono::milliseconds(5000));


    }

  // close filestreams and shut down server
  statefile.close();
  distancefile.close();
  server.Stop();
}

// MAIN

int main(int argc, char ** argv)
{
  try
    {
      RunServer();
    }

  catch (const std::exception & exc)
    {
      std::cout << exc.what() << std::endl;
    }

  return 0;
}
