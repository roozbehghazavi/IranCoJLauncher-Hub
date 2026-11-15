EmiterDef()
{
	LifeTime()
	{
		keyf(0, 1.4)
	}

	GenType("one_time")

	NumParticles()
	{
		randf(0, 7, 10)
	}

	StartVelocity()
	{
		keyf(0, 380)
	}

	StartVelocityRand()
	{
		keyv(0, 90, 220, 90)
	}

	Direction()
	{
		keyv(0, 0, -1, 0)
	}

	GenArea("point")

	CollisionAction("spawn_fx")
	{
		Trace("IRN_BloodDrip_trace.fx")
		Probability(0.6)
	}
}
