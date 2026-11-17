EmiterDef()
{
	LifeTime()
	{
		keyf(0, 1.5)
	}

	GenType("one_time")

	NumParticles()
	{
		randf(0, 1, 3)
	}

	StartVelocity()
	{
		keyf(0, 255)
	}

	StartVelocityRand()
	{
		keyv(0, 255, 0, 255)
	}

	Position()
	{
		keyv(0, 2, 0, 0)
	}

	Direction()
	{
		keyv(0, 0, -1, 0)
	}

	GenArea("point")

	CollisionAction("spawn_fx")
	{
		Trace("IRN_BloodDrip_trace.fx")
		Probability(0.7)
	}
}
