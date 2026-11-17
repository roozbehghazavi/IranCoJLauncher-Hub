EmiterDef()
{
	LifeTime()
	{
		keyf(0, 2)
	}

	GenType("one_time")

	NumParticles()
	{
		randf(0, 12, 22)
	}

	StartVelocity()
	{
		keyf(0, 550)
	}

	StartVelocityRand()
	{
		keyv(0, 55, 250, 55)
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
		Trace("IRN_BloodSplatter_trace.fx")
		Probability(0.6)
	}
}
