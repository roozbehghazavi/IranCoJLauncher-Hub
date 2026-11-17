EmiterDef()
{
	LifeTime()
	{
		keyf(0, 1.5)
	}

	GenType("one_time")

	NumParticles()
	{
		randf(0, 6, 10)
	}

	StartVelocity()
	{
		keyf(0, 400)
	}

	StartVelocityRand()
	{
		keyv(0, 40, 150, 40)
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
		Probability(1)
	}
}
