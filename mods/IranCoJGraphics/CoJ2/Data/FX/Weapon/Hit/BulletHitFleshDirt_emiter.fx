EmiterDef()
{
	LifeTime()
	{
		keyf(0, 1.5)
	}

	GenType("one_time")

	NumParticles()
	{
		keyf(0, 8)
	}

	StartVelocity()
	{
		keyf(0, 320)
	}

	StartVelocityRand()
	{
		keyv(0, 180, 220, 180)
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
