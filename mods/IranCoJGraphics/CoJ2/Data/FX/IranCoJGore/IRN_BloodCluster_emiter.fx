EmiterDef()
{
	LifeTime()
	{
		keyf(0, 1.8)
	}

	GenType("one_time")

	NumParticles()
	{
		randf(0, 12, 18)
	}

	StartVelocity()
	{
		keyf(0, 520)
	}

	StartVelocityRand()
	{
		keyv(0, 55, 240, 55)
	}

	Direction()
	{
		keyv(0, 0, -1, 0)
	}

	GenArea("point")

	CollisionAction("spawn_fx")
	{
		Trace("IRN_BloodSplatter_trace.fx")
		Probability(0.5)
	}
}
