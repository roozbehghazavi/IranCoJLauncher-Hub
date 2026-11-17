EmiterDef()
{
	LifeTime()
	{
		keyf(0, 1.5)
	}

	GenType("one_time")

	NumParticles()
	{
		keyf(0, 2)
	}

	StartVelocity()
	{
		keyf(0, 600)
	}

	StartVelocityRand()
	{
		keyv(0, 120, 0, 120)
	}

	Position()
	{
		keyv(0, 0, 10, 0)
	}

	Direction()
	{
		keyv(0, 0, -1, 0)
	}

	GenArea("point")

	CollisionAction("spawn_fx")
	{
		Trace("IRN_BloodSplatter_trace.fx")
		Probability(0.8)
	}
}
