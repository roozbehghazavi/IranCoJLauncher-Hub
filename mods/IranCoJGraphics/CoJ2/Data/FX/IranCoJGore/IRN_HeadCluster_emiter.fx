EmiterDef()
{
	LifeTime()
	{
		keyf(0, 3)
	}

	GenType("one_time")

	NumParticles()
	{
		keyf(0, 1)
	}

	StartVelocity()
	{
		keyf(0, 300)
	}

	StartVelocityRand()
	{
		keyv(0, 0, 120, 0)
	}

	Position()
	{
		keyv(0, 2, -40, 0)
	}

	Direction()
	{
		keyv(0, 0, -1, 0)
	}

	GenArea("point")

	CollisionAction("spawn_fx")
	{
		Trace("IRN_BloodPuddle_trace.fx")
		Probability(1)
	}
}
