EmiterDef()
{
	LifeTime()
	{
		keyf(0, 1)
	}

	GenType("one_time")

	NumParticles()
	{
		randf(0, 2, 4)
	}

	StartVelocity()
	{
		keyf(0, 170)
	}

	StartVelocityRand()
	{
		keyv(0, 60, 50, 60)
	}

	Direction()
	{
		keyv(0, 0, 1, 0)
	}

	GenArea("point")

	CollisionAction("spawn_fx")
	{
		Trace("IRN_BloodDrip_trace.fx")
		Probability(0.6)
	}
}
