# And AI said, Let there be Light.

Okay, moving from one rhetoric to another, how smart is your smart home device? I bought a smart-LED bulb which promised many-a feature. It delivered on the promises as well. After a year and a half of regular-use, I just realised I hadn’t utilised the full extent of its capabilities. And to put it in the words of Tyler the Creator - “I hate wasted potential, that sh*t crushes my spirit”.


Basically, the joy of switching colours lost to the tediousness of it, and the brightness wasn’t great either, so I found myself sticking to a larger stick/tube light. Not to punch down, but this light is a “dumb device” (a coinage I don’t necessarily agree with; it should be called a “smart-enough”device) only powered by a physical switch. The philistine I am, I read my books in bed. I need to get out, switch the lights off physically, and sleep. Not so optimal.

So I told myself - “I literally have a Claude subscription, I’m better than this.” Let’s take this from tool-shaped object ([read](https://x.com/willmanidis/status/2021655191901155534?s=46)) to tool with Archestra, agents and MCPs.

Programmatically controlling my Phillips WiZ light bulb was a solved problem. It communicates via simple UDP, and the pywizlight library provides a python abstraction over it. I made an MCP server out of it.

I looked up ways to automate the smart-enough stick light, and it’s essentially a switch bot controlled over Wi-Fi. Went to the electronics store and bought servo motors, an ESP32, several jumper cables and a MicroUSB data-transfer cable because the ones in my cable-stash were power only. Wrote an .ino program to “move” the servo motor, exposed the endpoints, wrote the MCP to toggle it and et-voila we’re through.

I added my servers to the MCP Registry on Archestra. Before I say how I did it, now would be a good time for me to reveal what exactly I did.

I made an AI Agent, that with the help of other subagents, orchestrates my lighting to literally make it feel like a living roommate. To give you an idea, here are something’s I make Switcheroo (what I call my agent) do.

- In one hour, check if i should exit my position on stock name. (The chat has context of my entry)
- Good morning, set me up.
- Fact-checking, but more dramatic: Is zohran the mayor of nyc?
- I’ve set my gravy to simmer remind me in 10 minutes.
- Do a status check on the latest workflow on repo repo name.

When I’m in too deep working or on a YouTube rabbit hole, no notification gets to me. Fortunately, the physical stimulus of my entire room changing appearance and the audio trigger of a switch clicking and a servo motor buzzing, make sure I get the message. To make sure I get the message, the large stick light shuts off, and the room is painted a certain color. A quick 30 seconds later, the large light comes back on and the reminder turns off.

It’s AI that helps me stay more present, and I find it pretty useful at that. I even envision my mother sending a message telling me - “The visitors have left, change lights” or "tell my son to get some sunlight" to my telegram bot.

A “head” agent recieved the telegram message. It decides which sub-agents to delegate to which tasks. I made sub-agents that handle their own domain and tools. Analyst is an agent that does web search through Tavily MCP. Timekeeper keeps track of time. There’s a GitHub agent and also a hardware agent that’s responsible for coordinating the switch and wiz. Pretty cool.

More [here](www.github.com/arjunmukeshh/switcheroo).
