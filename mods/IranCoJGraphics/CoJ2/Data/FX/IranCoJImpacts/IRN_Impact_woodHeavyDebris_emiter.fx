EmiterDef()
{
	LifeTime()
	{
		keyf(0, 1.3)
	}

	GenType("one_time")

	NumParticles()
	{
		randf(0, 8, 14)
	}

	StartVelocity()
	{
		keyf(0, 420)
	}

	StartVelocityRand()
	{
		keyv(0, 240, 220, 240)
	}

	Direction()
	{
		keyv(0, 0, 1, 0)
	}

	GenArea("point")
}
