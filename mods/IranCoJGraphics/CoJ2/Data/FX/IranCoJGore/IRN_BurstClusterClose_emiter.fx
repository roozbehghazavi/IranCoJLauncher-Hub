EmiterDef()
{
	LifeTime()
	{
		keyf(0, 2)
	}

	GenType("one_time")

	NumParticles()
	{
		keyf(0, 1)
	}

	StartVelocity()
	{
		keyf(0, 250)
	}

	StartVelocityRand()
	{
		keyv(0, 0, 0, 0)
	}

	Position()
	{
		keyv(0, 2, -25, 0)
	}

	Direction()
	{
		keyv(0, 0, -1, 0)
	}

	GenArea("point")

	CollisionAction("spawn_fx")
	{
		Trace("IRN_BloodSplatter_trace.fx")
		Probability(1)
	}
}
