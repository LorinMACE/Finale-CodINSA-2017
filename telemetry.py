import struct,json
from math import degrees

def toint(s): return struct.unpack("<i",s.read(4))[0]
def tofloat(s): return round(struct.unpack('f',s.read(4))[0],4)
def tostring(a,size): return a.read(size).split("\0")[0]
def formatAngle(a):
    a = degrees(a)
    if a < 0: a = -(-a)%360
    elif a > 0: a = a%360
    return round(a,2)-180

class telemetry:
    def __init__(self,s):
        #Header
        self.Title = tostring(s,32)
        self.Version = toint(s)
        self.Size = toint(s)

        #Update number
        self.UpdateNumber = toint(s)

        #Game state
        self.GameState = toint(s)
        self.GameplayVariant = tostring(s,64)
        self.MapId = tostring(s,64)
        self.MapName = tostring(s,256)
        s.read(128) #Empty

        #Race state
        self.RaceState = toint(s);
        self.Time = toint(s);
        self.NbRespawns = toint(s);
        self.NbCheckpoints = toint(s);
        self.CheckpointTimes = [toint(s) for i in range(125)]
        s.read(32) #Empty

        self.Timestamp = toint(s)
        self.DiscontinuityCount = toint(s) #Empty

        #Rotation
        self.Rotx = tofloat(s)
        self.Roty = tofloat(s)
        self.Rotz = tofloat(s)
        self.Rotw = tofloat(s)

        #Translation
        self.Posx = tofloat(s)
        self.Posy = tofloat(s)
        self.Posz = tofloat(s)

        #Vitesse
        self.Velocityx = tofloat(s)
        self.Velocityy = tofloat(s)
        self.Velocityz = tofloat(s)
        s.read(32)#empty

        self.LatestStableGroundContactTime = toint(s)

        #Vehicle State
        self.VehicleTimestamp = toint(s)

        self.VehicleInputSteer = tofloat(s)
        self.VehicleGasPedal = tofloat(s)
        self.VehicleInputIsBraking = toint(s)
        self.VehicleInputIsHorn = toint(s)

        #Engine
        self.EngineRpm = tofloat(s)
        self.EngineCurGear = toint(s)
        self.EngineTurboRatio = tofloat(s)
        self.EngineFreeWheeling = toint(s)

        self.WheelsIsGroundContact = [toint(s) for i in range(4)]
        self.WheelsIsSliping = [toint(s) for i in range(4)]
        self.WheelsDamperLen = [tofloat(s) for i in range(4)]
        self.WheelsDamperRangeMin = tofloat(s)
        self.WheelsDamperRangeMax = tofloat(s)

        self.RumbleIntensity = tofloat(s)

        self.SpeedMeter = toint(s)
        self.IsInWater = toint(s)
        self.IsSparkling = toint(s)
        self.IsLightTrails = toint(s)
        self.IsLightsOn = toint(s)
        self.IsFlying = toint(s)
        s.read(32)

        self.Yaw = formatAngle(tofloat(s))
        self.Pitch = formatAngle(tofloat(s))
        self.Roll = formatAngle(tofloat(s))

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True, indent=4)

    def getPosition(self):
        return { "x":self.Posx, "y":self.Posy, "z":self.Posz }

    def getVelocity(self):
        """
        "x":self.Velocityx,
        "y":self.Velocityy,
        "z":self.Velocityz,
        """
        return { "speed":self.SpeedMeter }

    def getRotation(self):
        """
        "quaternions":{
        "x":self.Rotx,
        "y":self.Roty,
        "z":self.Rotz,
        "w":self.Rotw
        },
        """
        return {
            "yaw":self.Yaw,
            "pitch":self.Pitch,
            "roll":self.Roll
        }

    def makeResponse(self):
        #On est pas en jeu
        if self.GameState == 1: return json.dumps({"Status":"Menu"}),200
        elif self.GameState == 3: return json.dumps({"Status":"Paused"}),200
        elif self.GameState != 2: return json.dumps({"Status":"Error"}),500

        #On est en jeu
        if self.RaceState == 0:
            return json.dumps({
                "Status":"BeforeStart",
                "MapId":self.MapId,
                "Position":self.getPosition(),
                "Rotation":self.getRotation()
            }),200
        elif self.RaceState == 2:
            return json.dumps({
                "Status":"Finished",
                "RaceTime":self.Time,
                "Respawns":self.NbRespawns
            }),200
        elif self.RaceState != 1: return json.dumps({"Status":"Error"}),500

        #On est en course
        return json.dumps(
            {   "Status":"Running",
                "Checkpoint":self.NbCheckpoints,
                "Respawns":self.NbRespawns,
                "Time":self.Time,
                "Position":{
                    "x":self.Posx,
                    "y":self.Posy,
                    "z":self.Posz
                },
                "Rotation":self.getRotation(),
                "SpeedMeter" : self.SpeedMeter,
                "Commands":{
                    "Direction":self.VehicleInputSteer,
                    "Braking":self.VehicleInputIsBraking,
                    "GasPedal":self.VehicleGasPedal,
                },
                "Engine":{
                    "Rpm":self.EngineRpm,
                    "CurrentGear":self.EngineCurGear,
                    "TurboRatio":self.EngineTurboRatio
                },
                "Vehicle":{
                    "Flying":self.IsFlying,
                    "Water":self.IsInWater,
                    "Sparkling":self.IsSparkling,
                    "SparklingIntensity":self.RumbleIntensity,
                    "LatestStableGroundContactTime":self.LatestStableGroundContactTime,
                    "Wheels":{
                        "Contact":{
                            "FL":self.WheelsIsGroundContact[0],
                            "FR":self.WheelsIsGroundContact[1],
                            "RR":self.WheelsIsGroundContact[2],
                            "RL":self.WheelsIsGroundContact[3]
                        },
                        "Sliping":{
                            "FL":self.WheelsIsSliping[0],
                            "FR":self.WheelsIsSliping[1],
                            "RR":self.WheelsIsSliping[2],
                            "RL":self.WheelsIsSliping[3]
                        }
                    }
                }
            }),200
