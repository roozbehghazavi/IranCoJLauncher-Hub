EmiterDef()
{
	LifeTime()
	{
		keyf(0, 2)
	}

	GenType("one_time")

	NumParticles()
	{
		randf(0, 18, 26)
	}

	StartVelocity()
	{
		keyf(0, 600)
	}

	StartVelocityRand()
	{
		keyv(0, 220, 260, 220)
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
		Probability(0.8)
	}
}
